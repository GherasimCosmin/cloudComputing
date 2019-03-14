
const http = require("http");
const fs = require('fs');
let MockDBFileName = './mockDb.json';


let rawdata = fs.readFileSync(MockDBFileName);
let mockDb = JSON.parse(rawdata);

http.createServer(function (request, response, error) {

    let pathAndValue = request.url.split("=");

    if (request.method === 'GET' && request.url === "/persons/getById=" + pathAndValue[1]) {

        if (pathAndValue[1].length > 0) {
            getById(response, request, parseInt(pathAndValue[1]));
        }

        response.statusCode = 400;
        response.end("Bad Request \nExample: /persons/getById=<number>")
    }

    if (request.method === 'GET' && request.url === '/persons/getAll') {
        getAll(response, request);
    }

    if (request.method === 'GET' && request.url === '/persons/getByHobby=' + pathAndValue[1]) {
        if (pathAndValue[1].length > 0) {
            getByHobby(response, request, pathAndValue[1]);
        }

        response.statusCode = 400;
        response.end("Bad Request \nExample: /persons/getByHobby=<hobby>")
    }

    if (request.method === 'POST' && request.url === '/persons/addNew') {
        addNew(response, request);
    }

    if (request.method === 'PUT' && request.url === '/persons/update') {
        update(response, request);
    }

    if (request.method === 'DELETE' && request.url === '/persons/delete=' + pathAndValue[1]) {

        if (pathAndValue[1].length > 0) {
            deletePerson(response, request, parseInt(pathAndValue[1]));
        }

        response.statusCode = 400;
        response.end("Bad Request \nExample: /persons/delete=<number>")
    }

    if (request.method === 'DELETE' && request.url === '/persons/getById') {

        response.statusCode = 400;
        response.end("Bad Request \nExample: /persons/getById=<number>")

    }

    if (request.method === 'DELETE' && request.url === '/persons/delete') {

        response.statusCode = 400;
        response.end("Bad Request \nExample: /persons/delete=<number>")

    }

    response.statusCode = 400;
    response.end("Bad Request \nAvaible Requests:\n\t/persons/getAll\n\t/persons/getById=<number>\n\t/persons/getByHobby=<hobby>\n\t/persons/addNew\n\t/persons/update\n\t/persons/delete=<number>")

}).listen(8889);

function responseHandler(response, request) {
    let body = '';
    request
        .on('error', (err) => {
            console.error(err);
        })
        .on('data', chunk => {
            body += chunk.toString();
        })
        .on('end', () => {
            responseHandler(body, response, request);
        });

    const { headers, method, url } = request;

    response.on('error', (err) => {
        console.error(err);
    });

    response.statusCode = 200;
    response.setHeader('Content-Type', 'application/json');
    body = JSON.parse(body);
    const responseBody = { headers, method, url, body };

    response.end(JSON.stringify(responseBody));
}
function getAll(response, request) {

    request.on('error', (err) => {
        console.error(err);
    }).on('end', (err) => {
        response.end(err);
    });

    response.on('error', (err) => {
        console.error(err);
    }).on('end', (err) => {
        response.end(err);
    });

    let body = {};
    body.personList = mockDb.personList;

    //db didn't supplied the list
    if (body.personList == null) {
        response.statusCode = 500;
        response.end("Data Base not active");
        return;
    }

    response.statusCode = 200;
    response.setHeader('Content-Type', 'application/json');

    response.end(body.personList);
}
function getById(response, request, id) {

    request.on('error', (err) => {
        console.error(err);
    }).on('end', (err) => {
        response.end(err);
    });

    response.on('error', (err) => {
        console.error(err);
    }).on('end', (err) => {
        response.end(err);
    });

    let body = {};
    body.personList = mockDb.personList;

    body.personList.forEach(element => {
        if (element.id === id) {
            body.response = element;
            return;
        }
    });

    if (body.response == null) {
        response.statusCode = 404;
        response.end("Person not found");
        return;
    }

    response.statusCode = 200;
    response.setHeader('Content-Type', 'application/json');

    response.end(JSON.stringify(body.response));
}
function addNew(response, request) {
    let body = '';
    response.on('error', (err) => {
        console.error(err);
    });

    request
        .on('error', (err) => {
            console.error(err);
        })
        .on('data', chunk => {
            body += chunk.toString();
        })
        .on('end', (err) => {
            body = JSON.parse(body);


            if (body == null) {
                response.statusCode = 400;
                response.end("Bad Request");
                return;
            }
            if (body.id == null) {
                response.statusCode = 400;
                response.end("Bad Request: id not provided");
                return;
            }
            if (body.name == null) {
                response.statusCode = 400;
                response.end("Bad Request: name not provided");
                return;
            }
            if (body.hobby == null) {
                response.statusCode = 400;
                response.end("Bad Request: hobby not provided");
                return;
            }

            let responseObject = {};
            responseObject.personList = mockDb.personList;

            responseObject.personList.forEach(element => {
                if (element.id == body.id) {
                    responseObject.person = element;
                    return;
                }
            });

            if (responseObject.person != null) {
                response.statusCode = 400;
                response.end("Person already in DB");
                return;
            }

            console.log("POST request\n" + body);
            mockDb.personList.push(body);

            const ModifiedDBToBeSaved = JSON.stringify(mockDb, null, 2);

            fs.writeFile(MockDBFileName, ModifiedDBToBeSaved, (err) => {
                if (err) {
                    response.statusCode = 500;
                    response.end("DB error");
                    throw err;
                }
                console.log('Data written to file');
            });

            response.statusCode = 200;
            response.setHeader('Content-Type', 'application/json');

            response.end("Person added to DB");
        });

}
function update(response, request) {
    let body = '';
    response.on('error', (err) => {
        console.error(err);
    });

    request
        .on('error', (err) => {
            console.error(err);
        })
        .on('data', chunk => {
            body += chunk.toString();
        })
        .on('end', (err) => {
            body = JSON.parse(body);


            if (body == null) {
                response.statusCode = 400;
                response.end("Bad Request");
                return;
            }
            if (body.id == null) {
                response.statusCode = 400;
                response.end("Bad Request: id not provided");
                return;
            }
            if (body.name == null) {
                response.statusCode = 400;
                response.end("Bad Request: name not provided");
                return;
            }
            if (body.hobby == null) {
                response.statusCode = 400;
                response.end("Bad Request: hobby not provided");
                return;
            }

            let responseObject = {};
            responseObject.personList = mockDb.personList;

            responseObject.personList.forEach(element => {
                if (element.id == body.id) {
                    responseObject.person = element;
                    return;
                }
            });

            if (responseObject.person == null) {
                response.statusCode = 400;
                response.end("Person not in DB");
                return;
            }

            console.log("DELETE request\n" + JSON.stringify(body.response));

            for (let i = 0; i < mockDb.personList.length; i++) {
                if (mockDb.personList[i].id == body.id) {
                    mockDb.personList[i] = body;
                    break;
                }
            }

            const ModifiedDBToBeSaved = JSON.stringify(mockDb, null, 2);

            fs.writeFile(MockDBFileName, ModifiedDBToBeSaved, (err) => {
                if (err) {
                    response.statusCode = 500;
                    response.end("DB error");
                    throw err;
                }
                console.log('Data written to file');
            });

            response.statusCode = 200;
            response.setHeader('Content-Type', 'application/json');

            response.end("Person updated");
        });

}
function deletePerson(response, request, id) {
    request.on('error', (err) => {
        console.error(err);
    }).on('end', (err) => {
        response.end(err);
    });

    response.on('error', (err) => {
        console.error(err);
    }).on('end', (err) => {
        response.end(err);
    });

    const { headers, method, url } = request;

    let body = {};
    body.personList = mockDb.personList;

    body.personList.forEach(element => {
        if (element.id === id) {
            body.response = element;
            return;
        }
    });

    if (body.response == null) {
        response.statusCode = 404;
        response.end("Person not found");
        return;
    }

    console.log("DELETE request\n" + JSON.stringify(body.response));

    for (let i = 0; i < mockDb.personList.length; i++) {
        if (mockDb.personList[i].id == body.response.id) {
            mockDb.personList.splice(i, i);
            break;
        }
    }

    const ModifiedDBToBeSaved = JSON.stringify(mockDb, null, 2);

    fs.writeFile(MockDBFileName, ModifiedDBToBeSaved, (err) => {
        if (err) {
            response.statusCode = 500;
            response.end("DB error");
            throw err;
        }
        console.log('Data written to file');
    });

    response.statusCode = 200;
    response.setHeader('Content-Type', 'application/json');

    response.end("Person deleted");
}
function getByHobby(response, request, hobby) {

    request.on('error', (err) => {
        console.error(err);
    }).on('end', (err) => {
        response.end(err);
    });

    response.on('error', (err) => {
        console.error(err);
    }).on('end', (err) => {
        response.end(err);
    });

    let body = {};
    body.personList = mockDb.personList;
    body.response = [];

    body.personList.forEach(element => {
        if (element.hobby === hobby) {
            body.response.push(element);
        }
    });

    if (body.response.length < 1) {
        response.statusCode = 404;
        response.end("No person with this hobby");
        return;
    }

    response.statusCode = 200;
    response.setHeader('Content-Type', 'application/json');

    response.end(JSON.stringify(body.response));
}
