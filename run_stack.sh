webserv="http://127.0.0.1:5000/api/v1/photomosaic/system/health_check" 

keyword="200" # enter the keyword for test content

COUNTER=0

function make_bucket() { awslocal s3 mb s3://$@ && awslocal s3api put-bucket-acl --bucket $@ --acl public-read;}

cd faas_stack
bash deploy_stack.sh --no-auth && 

while [  $COUNTER -lt 10 ]; do
    
    echo The counter is $COUNTER
    sleep 5
    if curl -i -s "$webserv" | grep "$keyword"
        then
        # if the keyword is in the content
        echo " the website is working fine"
        break
    else
        echo "Error";
        make_bucket images;
        let COUNTER=COUNTER+1
    fi
done

cd ..
faas-cli deploy
