serial=$1
series=$2

source ~/swift/read_only_creds
softlayer_images=$(swift list cloud-images -p $series/$serial/private | grep "softlayer.*vhd-0")
for f in $softlayer_images; do
    echo "Downloading $f"
    swift download cloud-images $f --skip-identical
    case $f in
        *"25G.vhd-0"*)
            name="ubuntu-$series-amd64-server-$serial-25G.vhd-0.vhd"
            ;;
        *"100G.vhd-0"*)
            name="ubuntu-$series-amd64-server-$serial-100G.vhd-0.vhd"
    esac
    echo "Extracting $f to $name"
    tar --sparse -O -xf $f > $name
    ls -al $name
    echo "Verifying file does not exist in ubuntu-cloud-images"
    #if aws --endpoint-url=https://s3.us-south.cloud-object-storage.appdomain.cloud --profile ibm-publish s3 ls s3://ubuntu-cloud-images/$name; then
        #"ERROR: File $name already exists. Skipping"
        #continue
    #fi
    echo "Pass"
    aws --endpoint-url=https://s3.us-south.cloud-object-storage.appdomain.cloud --profile ibm-publish s3 cp $name s3://ubuntu-cloud-images/
    echo "Verifying file does exist now"
    if ! aws --endpoint-url=https://s3.us-south.cloud-object-storage.appdomain.cloud --profile ibm-publish s3 ls s3://ubuntu-cloud-images/$name; then
        echo "ERROR: $name not found in ubuntu-cloud-images"
    fi
    echo "Pass"
    echo ""
    aws --endpoint-url=https://s3.us-south.cloud-object-storage.appdomain.cloud --profile ibm-publish s3 presign s3://ubuntu-cloud-images/$name --expires-in 1209600

done

