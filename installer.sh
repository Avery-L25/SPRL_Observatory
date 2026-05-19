#!/bin/bash

# ============================================
#todo future developments/additions/questions
#* camera setup
#? should there be user inputs? what should they be?
#? should this be a one stop shop? meaning code the services and scripts to
#? written in this .sh file
#! chmod for privilege 
# ============================================

set -e # exit on ERROR

HELP_TEXT="
Usage: bash getpython.sh [--version VERSION]

Options:
  --version               Which python version you'd like to install (e.g. 3.6.5, 3.9.5, 3.11.0)
  --help, -h              Show this help message
"
# ============================================
## Getting the user input
## Can be used to add configurations later!!!
# ============================================
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --help|-h)
    echo "$HELP_TEXT"
    exit 0
    ;;
    --version) VERSION="$2"; shift 2 ;;
    *) echo "Unknown option: $1" ;;
  esac
done

### TESTING STUFFFFFFF
echo $VERSION
dry_run=true
sleep_count=1
echo  dry_run = $dry_run

# ============================================
# Preparing to work with three scripts of the YooperNET Observatory
# ============================================
# The Camera, Magnetomer/Sensor, and File Manager Scripts will be colored as
# Red, Green, and Blue Respectively

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'


# ============================================
#! CONFIGURATION - CHANGE THESE VALUES
#todo update if multiple scripts
# ============================================
# Project Vars
PROJECT_NAME="SPRL_Observatory"
PROJECT_DIR="/opt/${PROJECT_NAME}"
VENV_NAME="venv"
VENV_DIR="${PROJECT_DIR}/$VENV_NAME"
GIT_REPO="https://github.com/Avery-L25/$PROJECT_NAME.git"
SERVICE_USER="python_service"

# Setup files
pkglist="dependencies.txt"
PYTHON_REQS="requirements.txt"

# Services / automation scripts
SERVICEFILE="yoopernet.service"
STARTER_SCRIPT="startup.sh"


# Helpful Functions
echo -e "\n ${BLUE}Log information will be output as blue${NC} \n $1"
log_info() {
    echo -e "\n${BLUE}[$1]${NC}\n"
}

log_success() {
    echo -e "\n${GREEN}[$1]${NC}\n"
}

log_error() {
    echo -e "\n${RED}[$1]${NC}\n"
}


# ============================================
# Upgrade system with necessary packages
# ============================================
if ! $dry_run; then
    exit
else
    log_error "This is a dry run testing purposes!"
    sleep sleep_count
fi

# 1: Update and Upgrade
log_info "Upgrade"
if ! $dry_run; then
    sudo apt-get upgrade 
fi
log_info  "Update"
if ! $dry_run; then
    sudo apt-get update -y
fi

# 2: Get dependencies
log_info "Getting Dependencies"
if ! $dry_run; then
    { # try

    sudo apt-get install $(cat pkglist)
    log_success "Success"
    #save your output

    } || { # catch
        log_error "Error"
        # save log for exception 
    }
fi


# ============================================
# Setup Python
# ============================================

# 1: Fetch Repository
log_info "Setting up Git Repository: \"$PROJECT_NAME\""
if !  $dry_run; then
    if [ -d "${PROJECT_DIR}/.git" ]; then
        log_info "Repository exists, continuing install."
    else
        log_info "Cloning repository."
        sudo git clone "${GIT_REPO}" "${PROJECT_DIR}"
    fi
fi

# 2: Create virtual Environment
log_info "Creating virtual python environmet $"
if !  $dry_run; then
    if [ -d "${VENV_DIR}" ]; then
        log_info "Virtual Environment \"$VENV_NAME\" exists, continuing install."
    else
        log_info "Cloning repository."
        sudo python -m venv "${VENV_DIR}"
    fi
fi

# 3: Install Libraries
log_info "Installing libaries for YooperNET from $PYTHON_REQS"
if !  $dry_run; then
    log_info "Cloning repository."
    pip install -r $PYTHON_REQS
fi

# TODO: Make section that assigns files to system (ie. yoopercam when called)

# TODO: Complicated zwo_asi_camera STUFFFFFFF if it needs that for the raspi still

# ============================================
# Setup Services for Scripts
# ============================================
