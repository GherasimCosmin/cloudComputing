 if(pathAndID.length > 1){
        if (request.method === 'GET' && request.url === ""+pathAndID[0]+pathAndID[1]) {
            console.log(pathAndID[1]);
            // getById(response, request,id);
            response.end(200);
        }
    }