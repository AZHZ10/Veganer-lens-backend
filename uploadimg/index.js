//import S3 from 'aws-sdk/clients/s3.js'; 
const aws = require("aws-sdk");
aws.config.update({
    accessKeyId:  'accessKeyId',
    secretAccessKey: 'secretAccessKey',
    region: "us-east-1",
});
exports.handler = (event, context, callback) => {
    //s3에 대한 접근 권한을 인증하기 위함
    const s3 = new aws.S3({ signatureVersion: 'v4' });
    const request = event;
    const filename = request.filename;
    const params = {
        Bucket: 'bucket-name',
        Key: `vmenu/${filename}`,
        Expires: 300,// In seconds
        ContentType: 'image/png'
    };
    s3.getSignedUrl("putObject", params, function(err, url){
    if(err) return callback(err);
    callback(null,{
      statusCode: 200,
      headers:{'Access-Control-Allow-Origin':'*'},
      body: url //생성 된 presigned URL을 프론트로 보냄
    });
  });
}
