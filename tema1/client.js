window.onload = setUp;
let span;
function setUp() {
   	span = document.getElementById('span');	
}

function firstService() {
    fetch('http://localhost:8085/service1')
        .then(function(response) {
            response.text()
                .then(function(value) {
                    span.innerHTML = value;
                });
        });
}

function secondService() {
    fetch('http://localhost:8085/service2')
        .then(function(response) {
            response.text()
                .then(function(value) {
                    span.innerHTML = value;
                });
        });
}

function thirdService() {
    fetch('http://localhost:8085/service3')
        .then(function(response) {
            response.text()
                .then(function(value) {
                    span.innerHTML = value;
                });
        });
}