# Use the latest Python image
FROM python:latest

# Add repository for additional packages
RUN printf "\ndeb https://deb.debian.org/debian bookworm contrib non-free\n" >> /etc/apt/sources.list

# Update and upgrade apt packages
RUN apt-get -y update && \
    apt-get -y upgrade

# Install required packages
RUN apt-get --no-install-recommends install -y \
    nano nodejs libgif-dev lsb-release software-properties-common \
    autoconf automake build-essential cmake git-core libass-dev libfreetype6-dev libgnutls28-dev libmp3lame-dev libsdl2-dev libtool libva-dev libvdpau-dev libvorbis-dev libxcb1-dev libxcb-shm0-dev libxcb-xfixes0-dev meson ninja-build pkg-config texinfo wget yasm zlib1g-dev \
    libunistring-dev libaom-dev libdav1d-dev libsvtav1enc-dev libdav1d-dev libopus-dev libfdk-aac-dev libvpx-dev libx265-dev libnuma-dev libx264-dev nasm \
    ninja-build build-essential pkg-config bc \
    libcgif-dev libfftw3-dev libopenexr-dev libgsf-1-dev libglib2.0-dev liborc-dev libopenslide-dev libmatio-dev libwebp-dev libjpeg-dev libexpat1-dev libexif-dev libtiff5-dev libcfitsio-dev libpoppler-glib-dev librsvg2-dev libpango1.0-dev libopenjp2-7-dev libimagequant-dev \
    fuse libfuse2 \
    fonts-noto

# Remove unnecessary package
RUN apt-get remove -y fonts-noto-color-emoji

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the application
CMD ["python", "bot.py"]
