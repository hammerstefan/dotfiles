#! /bin/bash
set -x
serial=$1
suite=$2

source ~/swift/read_only_creds
softlayer_images=$(swift -V 3 list cloud-images -p $suite/$serial/private | grep "ibm-guest.*.qcow2.tar.gz")
for f in $softlayer_images; do
    echo "Downloading $f"
    swift -V 3 download cloud-images $f --skip-identical
    case $f in
        *"100G.qcow2"*)
            name="ubuntu-$suite-amd64-server-$serial-100G.qcow2"
            ;;
    esac
    echo "Extracting $f to $name"
    tar --sparse -O -xf $f > $name
    ls -al $name
    echo "Verifying file does not exist in ubuntu-cloud-images"
    if aws --endpoint-url=https://s3.us-south.cloud-object-storage.appdomain.cloud --profile ibm-publish s3 ls s3://ubuntu-cloud-images/$name; then
        aws --endpoint-url=https://s3.us-south.cloud-object-storage.appdomain.cloud --profile ibm-publish s3 rm s3://ubuntu-cloud-images/$name
        echo "WARNING: File $name already exists. Skipping upload."
    else
        echo "Pass"
        aws --endpoint-url=https://s3.us-south.cloud-object-storage.appdomain.cloud --profile ibm-publish s3 cp $name s3://ubuntu-cloud-images/
        echo "Verifying file does exist now"
        if ! aws --endpoint-url=https://s3.us-south.cloud-object-storage.appdomain.cloud --profile ibm-publish s3 ls s3://ubuntu-cloud-images/$name; then
            echo "ERROR: $name not found in ubuntu-cloud-images"
        fi
        echo "Pass"
    fi
    echo "Generating presigned URL:"
    aws --endpoint-url=https://s3.us-south.cloud-object-storage.appdomain.cloud --profile ibm-publish s3 presign s3://ubuntu-cloud-images/$name --expires-in 1209600

done

