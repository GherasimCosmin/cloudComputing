const http = require('http');
let https = require('https');
const request = require('request');
const uuidv4 = require('uuid/v4');
'use strict';
const Search = require('azure-cognitiveservices-imagesearch');
const CognitiveServicesCredentials = require('ms-rest-azure').CognitiveServicesCredentials;

let serviceKey = "745c86f5437846e99da5281b12d910f0";
let credentials = new CognitiveServicesCredentials(serviceKey);
const ImageSearchAPIClient = require('azure-cognitiveservices-imagesearch');
let imageSearchApiClient = new ImageSearchAPIClient(credentials);

const subscriptionKey = "7f0f3f2ddb344b788f88a73cb39e55c1";
const analyzeImageKey = "cd5d9e7533a74bbaac3932bc41d02ac0";
const faceDetectionKey = "a33f641bfd2a479c9b218fd574fbdc8f";
const spellCheckKey = "a83efffdb80b4fe6bfb67d494362343f";
if (!subscriptionKey) {
    throw new Error('Environment variable for your subscription key is not set.')
};
const server = http.createServer((req, response, error) => {

    if (req.method === 'GET' && req.url === "/test") {
        response.statusCode = 200;
        response.end("Home");
        return;
    }

    if (req.method === 'POST' && req.url === "/translate") {
        translate_text(req, response);
    }

    if (req.method === 'POST' && req.url === "/searchImage") {
        search_image(req, response);
    }

    if (req.method === 'POST' && req.url === "/analyzeImage") {
        analyze_image(req, response);
    }

    if (req.method === 'POST' && req.url === "/faceDetection") {
        face_detection(req, response);
    }
    if (req.method === 'POST' && req.url === "/spellCheck") {
        spell_check(req, response);
    }

});
function translate_text(req, response) {
    let options = {
        method: 'POST',
        baseUrl: 'https://api.cognitive.microsofttranslator.com/',
        url: 'translate',
        qs: {
            'api-version': '3.0',
            'to': 'de'
        },
        headers: {
            'Ocp-Apim-Subscription-Key': subscriptionKey,
            'Content-type': 'application/json',
            'X-ClientTraceId': uuidv4().toString()
        },
        body: [{
            'text': 'Hello World!'
        }],
        json: true,
    };
    let body = '';
    req.on('error', (err) => {
        console.error(err);
    })
        .on('data', chunk => {
            body += chunk.toString();
        })
        .on('end', (err) => {
            try {
                body = JSON.parse(body);
            }
            catch (e) {
                response.statusCode = 400;
                response.end("Bad Request");
                return;
            }
            console.log(body);
            options.qs.to = body.lang;
            options.body[0].text = body.text;

            request(options, (err, res, body) => {
                response.statusCode = 200;
                response.setHeader('Content-Type', 'application/json');
                response.end(JSON.stringify(body, null, 4));
            });
        });
}
function search_image(req, response) {
    let body = '';
    req.on('error', (err) => {
        console.error(err);
    })
        .on('data', chunk => {
            body += chunk.toString();
        })
        .on('end', (err) => {
            try {
                body = JSON.parse(body);
            }
            catch (e) {
                response.statusCode = 400;
                response.end("Bad Request");
                return;
            }
            searchTerm = body.text;
            sendQuery(searchTerm).then(imageResults => {
                if (imageResults == null) {
                    console.log("No image results were found.");
                }
                else {
                    console.log(`Total number of images returned: ${imageResults.value.length}`);
                    let firstImageResult = imageResults.value[0];
                    console.log(`Total number of images found: ${imageResults.value.length}`);
                    console.log(`Copy these URLs to view the first image returned:`);
                    console.log(`First image thumbnail url: ${firstImageResult.thumbnailUrl}`);
                    console.log(`First image content url: ${firstImageResult.contentUrl}`);
                    response.statusCode = 200;
                    response.setHeader('Content-Type', 'application/json');
                    response.end(JSON.stringify(firstImageResult.contentUrl));
                }
            })
                .catch(err => console.error(err))
        });
}
function analyze_image(req, response) {
    const uriBase = 'https://westeurope.api.cognitive.microsoft.com/vision/v2.0/analyze';
    const params = {
        'visualFeatures': 'Categories,Description,Color',
        'details': '',
        'language': 'en'
    };
    const options = {
        uri: uriBase,
        qs: params,
        body: '{"url": ' + '"' + '"}',
        headers: {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': analyzeImageKey
        }
    };
    let body = '';
    req.on('error', (err) => {
        console.error(err);
    })
        .on('data', chunk => {
            body += chunk.toString();
        })
        .on('end', (err) => {
            try {
                body = JSON.parse(body);
            }
            catch (e) {
                response.statusCode = 400;
                response.end("Bad Request");
                return;
            }
            options.body = '{"url": ' + '"' + body.url + '"}'
            request.post(options, (error, res, body) => {
                if (error) {
                    console.log('Error: ', error);
                    return;
                }
                response.statusCode = 200;
                response.end(JSON.stringify(JSON.parse(body), null, '  '));
            });
        });
}
function face_detection(req, response) {
    const uriBase = 'https://westeurope.api.cognitive.microsoft.com/face/v1.0/detect';
    const params = {
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,' +
            'emotion,hair,makeup,occlusion,accessories,blur,exposure,noise'
    };

    const options = {
        uri: uriBase,
        qs: params,
        body: '{"url": ' + '"' + '"}',
        headers: {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': faceDetectionKey
        }
    };
    let body = '';
    req.on('error', (err) => {
        console.error(err);
    })
        .on('data', chunk => {
            body += chunk.toString();
        })
        .on('end', (err) => {
            try {
                body = JSON.parse(body);
            }
            catch (e) {
                response.statusCode = 400;
                response.end("Bad Request");
                return;
            }
            options.body = '{"url": ' + '"' + body.url + '"}'
            request.post(options, (error, res, body) => {
                if (error) {
                    console.log('Error: ', error);
                    return;
                }
                response.statusCode = 200;
                response.end(JSON.stringify(JSON.parse(body), null, '  '));
            });
        });
}
function spell_check(req, response) {
    let host = "api.cognitive.microsoft.com";
    let mkt = "en-US";
    let mode = "proof";
    let path = "/bing/v7.0/spellcheck?mkt=" + mkt + "&mode=" + mode + "&text=";
    let request_params = {
        method: 'GET',
        hostname: host,
        path: path,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': 0,
            'Ocp-Apim-Subscription-Key': spellCheckKey,
        }
    };
    let body = '';
    req.on('error', (err) => {
        console.error(err);
    })
        .on('data', chunk => {
            body += chunk.toString();
        })
        .on('end', (err) => {
            try {
                body = JSON.parse(body);
            }
            catch (e) {
                response.statusCode = 400;
                response.end("Bad Request");
                return;
            }
            request_params.headers["Content-Type"] = body.text.length + 5;
            console.log( body.text.replace(/(?=[() ])/g, '%20'));
            request_params.path = request_params.path + body.text.replace(' ','%20');
            let req = https.request(request_params, (res) => {
                let body = '';
                res.on('data', function (d) {
                    body += d;
                });
                res.on('end', function () {
                    console.log(body);
                    response.statusCode = 200;
                    response.end(body)
                });
                res.on('error', function (e) {
                    console.log('Error: ' + e.message);
                });
            });
            req.end();
        });
}
const sendQuery = async (searchTerm) => {
    return await imageSearchApiClient.imagesOperations.search(searchTerm);
};

const port = process.env.PORT || 1337;
server.listen(port);

console.log("Server running at http://localhost:%d", port);
