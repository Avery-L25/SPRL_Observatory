import typing
import toml
from pathlib import Path
from typing import Optional, Mapping, List, Dict
from bindings import Controllable, Camera, get_nb_cameras, get_sdk_version
from Sensors.camera.roi import ROI
from Sensors.camera.image import Image


class Camera(Camera):
    """
    Interface to a ASI ZWO Camera.
    Index: index of the camera, if several are plugged.
    To get the number of cameras detected, call
    camera_zwo_asi.get_nb_cameras().

    Arguments:
      index: index of the camera (use 0 if only one camera is plugged)
    """

    def __init__(self, index: int) -> None:

        # no idea why, camera may not be detected if this is not
        # called first
        nb_detected_cams = get_nb_cameras()
        super().__init__(index)

    def set_control(self, controllable: str,
                    value: typing.Union[int, str]) -> None:
        """
        Set the value of the controllable.

        Arguments:
          controllable: the parameter to update
          value: either an int, or "auto"
        """
        if isinstance(value, str):
            if value != "auto":
                raise ValueError(
                    f"can not set {value} as camera controllable value: "
                    f"only an int or 'auto' accepted"
                )
            super().set_auto(controllable)
            return
        super().set_control(controllable, value)

    def get_controls(self) -> typing.Dict[str, Controllable]:
        """
        Returns the current values of all controllables
        """
        return super().get_controls()

    def configure_from_toml(
        self, config: typing.Union[Path, typing.Mapping[str, typing.Any]]
    ) -> None:
        """
        Configure the camera using a TOML formated configuration file.
        To get an example configuration file: see the method
        Camera.to_toml.
        To request a controllable to be automatically set, use the string
        'auto' in the TOML configuration.
        """
        if isinstance(config, str):
            config = Path(config)
        if isinstance(config, Path):
            # checking file exists
            if not config.is_file():
                raise FileNotFoundError(
                    f"failed to configure camera from {config}: file not found"
                )

            # parsing file
            content = toml.load(config)

        else:
            content = config

        # making sure it has content for both controllables and ROI
        required_keys = ("controllables", "roi")
        for rk in required_keys:
            if rk not in content:
                raise ValueError(
                    f"toml camera configuration {config} is missing the "
                    f"key {rk}"
                )

        # reading values for controllables
        controllables = content["controllables"]

        # reading values from ROI
        roi = ROI.from_toml(content["roi"])
        issues = roi.check(self.get_info())
        if issues:
            issues_str = ", ".join(issues)
            raise ValueError(
                "The provided TOML file is not suitable for configuring the "
                f"camera: {issues_str}"
            )

        # creating and returning instance
        for controllable, value in controllables.items():
            if isinstance(value, str) and value == "auto":
                self.set_auto(controllable)
            else:
                self.set_control(controllable, value)
        self.set_roi(roi)

    def to_dict(
            self,
            specify_auto: bool = True,
            non_writable: bool = False,
    ) -> typing.Dict[str, typing.Any]:
        """
        Return a dictionary representation of the
        current configuration of the camera, with the
        keys "roi" and the key "controllables".
        """
        d: typing.Dict[str, typing.Any] = {}
        controllables: typing.Dict[str, typing.Any] = {}
        for key, controllable in self.get_controls().items():
            if non_writable or controllable.is_writable:
                if specify_auto and controllable.is_auto:
                    controllables[key] = "auto"
                else:
                    controllables[key] = controllable.value
        d["controllables"] = controllables

        roi = self.get_roi()
        attributes = ("start_x", "start_y", "width", "height", "bins")
        roi_d = {attr: getattr(roi, attr) for attr in attributes}
        roi_d["type"] = roi.type.name
        d["roi"] = roi_d

        return d

    def to_toml(
        self,
        path: Optional[Path] = None,
        specify_auto: bool = True,
        non_writable: bool = False,
    ) -> Optional[str]:
        """
        Dump the current configuration of the camera to a file. To change
        the camera's configuration, you may update
        this file and call the method Camera.configure_from_toml.

        Returns:
          a toml formatted string if path is None, else None
        """

        d = self.to_dict(specify_auto, non_writable)

        controllables = {}
        for key, controllable in self.get_controls().items():
            if non_writable or controllable.is_writable:
                if specify_auto and controllable.is_auto:
                    controllables[key] = "auto"
                else:
                    controllables[key] = controllable.value
        d["controllables"] = controllables

        roi = self.get_roi()
        attributes = ("start_x", "start_y", "width", "height", "bins")
        roi_d = {attr: getattr(roi, attr) for attr in attributes}
        roi_d["type"] = roi.type.name
        d["roi"] = roi_d

        if path is not None:
            with open(path, "w+") as f:
                toml.dump(d, f)
        else:
            return toml.dumps(d)

    def get_roi(self) -> ROI:
        """
        Return the current ROI of the camera.
        """
        bindings_roi = super().get_roi()
        roi = ROI()
        for attr in ("start_x", "start_y", "width", "height", "type", "bins"):
            setattr(roi, attr, getattr(bindings_roi, attr))
        return roi

    def _check_controllable(self, controllable: Controllable) -> Optional[str]:
        """
        Check if the controllable is suitable, i.e. can be used to configure
        the camera.
        """
        if not controllable.is_writable:
            return None
        if controllable.is_auto and not controllable.supports_auto:
            return (f"controllable {controllable.name} is set to auto, but " +
                    "that is not supported")
        if controllable.value > controllable.max_value:
            return (f"controllable {controllable.name} has value "
                    f"{controllable.value} > max value "
                    f"{controllable.max_value}")
        if controllable.value < controllable.min_value:
            return (f"controllable {controllable.name} has value "
                    f"{controllable.value} < min value "
                    f"{controllable.min_value}")
        return None

    def configure(self, roi: ROI, controllables: Dict[str, Controllable]
                  ) -> None:
        """
        Configure the camera, setting up the ROI (Region Of Interest) and
        values for the controllable.

        Arguments:
          roi: instance of ROI
          controllables: dictionary with keys are string that must correspond
                         to controllables supported by the camera. To get a
                         list of supported controllables, print an instance of
                         Camera. The printed string will provided information
                         about supported controllable, including the min and
                         max values; and if 'auto' values are supported.
        """
        issues = roi.check(self.get_info())
        opt_controllable_issues: List[Optional[str]] = [
            self._check_controllable(controllable)
            for controllable in controllables.values()
        ]
        controllable_issues: List[str] = [
            issue for issue in opt_controllable_issues if issue is not None
        ]
        issues += controllable_issues
        if issues:
            issues_str = ", ".join(issues)
            raise ValueError(f"failed to configure camera: {issues_str}")
        self.set_roi(roi)
        for key, controllable in controllables.items():
            if controllable.is_writable:
                if controllable.is_auto:
                    self.set_auto(key)
                else:
                    self.set_control(key, controllable.value)

    def capture(
        self,
        image: Optional[Image] = None,
        filepath: Optional[Path] = None,
        show: bool = False,
    ) -> Image:
        """
        Take a picture. Either fill the image passed as argument, or
        create a new one. If an image is passed as argument, it should be
        of a size suitable for the requested ROI. To get an image of the
        correct size, call "image = camera.get_roi().get_image()". If filepath
        is not None, the image is saved to file. If show is True, the image is
        displayed (opencv window).
        """

        if image is None:
            image = self.get_roi().get_image()

        super().capture(image.get_data(), image.get_data_size())

        if filepath is not None:
            image.save(filepath)

        if show:
            image.display(label=self.get_info().name)

        return image

    def __str__(self) -> str:
        def _same_length(items: typing.Iterable[str]) -> typing.List[str]:
            max_len = max([len(item) for item in items])
            return [item + " " * (max_len - len(item)) for item in items]

        def _str_control(control: Controllable) -> str:
            name = control.name
            writable = "(w)" if control.is_writable else " " * 3
            auto = (
                "(auto)"
                if control.is_auto
                else ("(as)  " if control.supports_auto else " " * 6)
            )
            return f"|{writable}{auto} {name}"

        r = [f"asi sdk: {get_sdk_version()}"]
        r.append(str(self.get_info()))

        controls = self.get_controls().values()

        names = _same_length(
            ["|controllable", "-" * 13] + list((map(_str_control, controls)))
        )
        values = _same_length(
            ["|value", "-" * 6] + [f"|{str(control.value)}" for control in
                                   controls]
        )
        mins = _same_length(
            ["|min value", "-" * 10]
            + [f"|{str(control.min_value)}" for control in controls]
        )
        maxs = _same_length(
            ["|max value", "-" * 10]
            + [f"|{str(control.max_value)}" for control in controls]
        )

        for name, value, min_, max_ in zip(names, values, mins, maxs):
            r.append("\t".join([name, value, min_, max_]))

        r.append(
            "|legend: (w): is writable, (auto): in auto mode, (as): auto mode"
            "not active but supported\n"
        )

        return "\n".join(r)
