const BosClient = require('./src/bos_client');

const client = new BosClient({
    endpoint: 'https://bj.bcebos.com',
    credentials: {
        ak: '113b77508e0346aa9442e445461cb6ec',
        sk: '34c4c96b70574d939983f13e9c4d1a0d'
    }
});

const targetBucket = 'bce-bos-client';
const targetKey = 'b';
const sourceBucket = 'bce-bos-client';
const sourceKey = 'a';

client.initiateMultipartUpload(targetBucket, targetKey).then(res => {
    let size = 4273130;
    const tasks = [];
    const uploadId = res.body.uploadId;
    const MAX_PUT_OBJECT_LENGTH = 1048576; // 1m

    while(size > 0) {
        const begin = tasks.length * MAX_PUT_OBJECT_LENGTH;
        const end = size > MAX_PUT_OBJECT_LENGTH
            ? tasks.length * MAX_PUT_OBJECT_LENGTH + MAX_PUT_OBJECT_LENGTH - 1
            : tasks.length * MAX_PUT_OBJECT_LENGTH + size - 1

        tasks.push(`${begin}-${end}`);
        size -= MAX_PUT_OBJECT_LENGTH;
    }

    return Promise.all(tasks.map((range, index) => client.uploadPartCopy(
        sourceBucket, sourceKey, targetBucket, targetKey, uploadId, index + 1, range
    ))).then(res => client.completeMultipartUpload(
        targetBucket, targetKey, uploadId,
        res.map((item, index) => {
            return Object({
                partNumber: index + 1,
                eTag: item.body.eTag
            })
        })
    ))
}).then(
    res => {debugger},
    err => {debugger}
)
// client.copyObject(
//     "haokan-video", "版权长视频/电视剧/包青天之白玉堂传/视频/012.mp4", "haokan-video", "版权长视频/电视剧/包青天之白玉堂传奇/视频/012.mp4"
// ).then(
//     res => console.log(res),
//     err => console.log(JSON.stringify(err))
// )