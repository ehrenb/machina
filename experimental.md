## Android Emulation

This is a work-in-progress feature.

### Virtual Machine notes
    
* If installing on VirtualBox guest, be aware that, while nested virtualization is available, it only works on a few select CPUs.  Nested virtualization is required to run KVM inside of a VM.  KVM is required by [docker-emulator-android](https://github.com/agoda-com/docker-emulator-android) 
* If installing on VMware guest, nested virtualization is supported and works without issue. VMware Workstation Player (free) or VMware Fusion (paid) is recommended over Virtualbox.

### Installation

1.  If using any of the Worker Modules that do dynamic testing on an Android emulator via the Host's docker socket, you'll need to install kvm on your host.  Android Emulation on Linux uses KVM for hardware acceleration on x86/64

    ```bash
    apt-get install qemu-kvm libvirt-bin virtinst bridge-utils cpu-checker
    ```
    
2.  Clone [docker-emulator-android](https://github.com/agoda-com/docker-emulator-android) and build:

    ```bash
    git clone https://github.com/agoda-com/docker-emulator-android.git
    cd docker-emulator-android
    make build
    ```
