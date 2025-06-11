import os
from pathlib import Path
from Sensors.camera.camera import Camera
from bindings import get_nb_cameras, create_udev_file

_CONFIG_FILE = "zwo_asi.toml"


def shot():

    index = 0
    print(f"opening camera {index}")
    camera = Camera(index)

    # is there a configuration file in the current directory?
    config_path = Path(os.getcwd()) / _CONFIG_FILE
    # if config_path.is_file() and not args.noconfig:
    print(f"configuring using {config_path}")
    camera.configure_from_toml(config_path)

    # taking the picture
    print("taking picture")
    image = camera.capture()

    # saving the picture
    save_path = r'test.jpg'
    print(f"saving to {save_path}")
    image.save(save_path)

    # print(camera.get_controls())
    # camera.to_toml('camera.toml')
    return image.get_image()


shot()
