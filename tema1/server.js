const http = require('http');
const request = require('request');
const url = require('url');
const data = require('./config.json');

http.createServer(function(req, res) {
    let q = url.parse(req.url, true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    //routing
    if (q.pathname === "/service1") {

        request.get(`https://api.nytimes.com/svc/books/v3/lists/current/hardcover-fiction.json?api-key=${data.firstSercviceApi}`, { json: true },
            (error, r, body) => {
                if (error) {
                    console.error(error)
                    return
                }
                console.log(body.results.books[2]);
                res.write(body.results.books[1].rank.toString(), function() { res.end(); });
            })
    }
    if (q.pathname === "/service2") {
        request.get('https://en.wikipedia.org/w/api.php?action=parse&page=Lion&format=json', { json: true },
            (error, r, body) => {
                if (error) {
                    console.error(error)
                    return
                }
                console.log(body.parse.title);
                res.write(body.parse.title, function() { res.end(); });
            })
    }
    if (q.pathname === "/service3") {
        request.get(`https://api.nytimes.com/svc/books/v3/lists/current/hardcover-fiction.json?api-key=${data.firstSercviceApi}`, { json: true },
            (error, r, body) => {
                if (error) {
                    console.error(error)
                    return
                }
                let serv1 = body.results.books[2];
                request.get('https://en.wikipedia.org/w/api.php?action=parse&page=Lion&format=json', { json: true },
                    (error, r, body) => {
                        if (error) {
                            console.error(error)
                            return
                        }
                        let serv2 = body.parse.title;
                        request.get(`http://www.omdbapi.com/?t=${serv2}&page=2&apikey=${data.thirdSercviceApi}`, { json: true },
                            (error, r, body) => {
                                if (error) {
                                    console.error(error)
                                    return
                                }
                                res.write(JSON.stringify(body), function() { res.end(); });
                            })
                    })
            })
    }
}).listen(8085);