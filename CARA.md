# Extracting an OVA File
To convert a virtual machine from OVA format, it is first necessary to extract the files that the OVA file contains. On the Linux command line, this can be done using the tar command, like this:
```shell
tar xvf some_virtual_machine.ova
```
Inside the OVA archive, you will find an OVF file and a VMDK file. The VMDK file is normally in a “stream” format that is not suitable for direct use with a virtual machine. Instead, it should be converted to qcow2 format with qemu-img:
``` shell
qemu-img convert -f vmdk -O qcow2 input.vmdk output.qcow2
```

running

```shell
qemu-system-x86_64 -m 256 -hda MikroTik-RouterOS-6.40.5-disk1.qcow2 -nographic -net nic,model=virtio -net user,hostfwd=tcp::8022-:22,hostfwd=tcp::8291-:8291
```