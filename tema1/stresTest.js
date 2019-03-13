const request = require('request');
function boom(){
	for(let i=0;i<50;i++){
		 request.get('http://localhost:8085/service1', { json: true },
            (error, r, body) => {
                if (error) {
                    console.error(error)
                    return
                }
                console.log(body);
            });
	}
}
boom();