# Extracting an OVA File
To convert a virtual machine from OVA format, it is first necessary to extract the files that the OVA file contains. On the Linux command line, this can be done using the tar command, like this:
```shell
tar xvf some_virtual_machine.ova
```
Inside the OVA archive, you will find an OVF file and a VMDK file. The VMDK file is normally in a “stream” format that is not suitable for direct use with a virtual machine. Instead, it should be converted to qcow2 format with qemu-img:
``` shell
qemu-img convert -f vmdk -O qcow2 input.vmdk output.qcow2
```