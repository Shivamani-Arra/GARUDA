// const { response } = require("express");

// script.js

const socket = io();
// const socket = io("http://192.168.13.123:5000");
socket.on('connect',function(){
    console.log(`connected with socket ID : ${socket.id}`);
});
$(document).ready(function() {
    var altimeter1 = $.flightIndicator('#altimeter1', 'altimeter');
    // altimeter1.setAltitude(0);
    socket.on('alt', function(data) {
        console.log('Received altitude update:', data.data);
        const altitudeInFeet = data.data * 3.28084;
        altimeter1.setAltitude(altitudeInFeet);
        document.querySelector("#altitude1_dis").innerHTML="Altitude : "+data.data+" m";
    });
    
})



$(document).ready(function() {
    var heading1 = $.flightIndicator('#heading1', 'heading');
    // heading1.setHeading(0);
    socket.on('yaw', function(data) {
        heading1.setHeading(data.data);
        document.querySelector("#heading1_dis").innerHTML="YAW : "+data.data;
    });
    
})



function getData() {
    console.log("HOOO");
    fetch('/getData', {
        method: 'POST',
    })
    .then(response => response.json()
    )
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function takeOff(event) {
    event.preventDefault();
    const altitude = document.getElementById('altitude').value;
    console.log(altitude);
    fetch('/main', {
        method: 'POST',
        body: JSON.stringify({ altitude: altitude }),
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        // console.log(data,"HIII");
        window.location.href = "/index.html";
    })
    .catch(error => {
        
        window.location.href = "/index";
        console.error('Error:', error);
    });
}
function GoTo(event){
    event.preventDefault();
    const altitude = document.getElementById('altitude').value;
    console.log(altitude);
    fetch('/main', {
        method: 'POST',
        body: JSON.stringify({ altitude: altitude }),
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log(data,"HIII");
        // window.location.href = "/index.html";
    })
    .catch(error => {
        
        // window.location.href = "/index";
        console.error('Error:', error);
    });
}
function Land() {
    fetch('/Land')
    .then(response => response.json())
    .then(data => {
        console.log("Hello");
        console.log(data);
    })
    .catch(error => {
        console.log("Hello");
        console.error('Error:', error);
    });
}


function RTL() {
    fetch('/return_to_home', {
        method: 'POST',
        body: JSON.stringify({ alt: 0 }),
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log("HIIIIIIIIIIIIIIIIIIII");
        window.location.href = "/";
        console.log(data);
    })
    .catch(error => {
        console.log("2345678HIIIIIIIIIIIIIIIIIIII");
        window.location.href = "/";
        // console.error('Error:', error);
    });
}


function chageyaw(event) {
    event.preventDefault();
    const yaw = document.getElementById('yaw').value;
    console.log(yaw);
    fetch('/change_yaw', {
        method: 'POST',
        body: JSON.stringify({ yaw: yaw }),
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
        // window.location.href = "/index";
    });
}

function speedtest() {
    fetch('/networkspeed', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        
        const downloadspeed = Math.floor(data.download_speed);
        document.querySelector("#Downloadspeed").innerHTML="Download Speed : "+downloadspeed;
        console.log(downloadspeed);
        const uploadspeed = Math.floor(data.upload_speed);
        document.querySelector("#Uploadspeed").innerHTML="Upload Speed : "+uploadspeed;
        console.log(uploadspeed);


        $(document).ready(function() {
            $("#demo1").gauge(uploadspeed, {
                min: 0,
                max: 100,
                unit: " Mpbs",
                color: "red",
                colorAlpha: 1,
                bgcolor: "#222",
                type: "default"
            });
        
            $("#demo2").gauge(downloadspeed, {
                min: 0,
                max: 100,
                unit: " Mpbs",
                color: "green",
                colorAlpha: 1,
                bgcolor: "#222",
                type: "default"
            });
        });

    })
    .catch(error => {
        console.error('Error:', error);
    });
}




// const socketc = io("http://172.168.0.179:5000");
// socketc.on('connect',function(){
//     console.log(`connected with socket ID 1 : ${socketc.id}`);
// });

// $(document).ready(function() {
//     var altimeter2 = $.flightIndicator('#altimeter2', 'altimeter');
//     altimeter2.setAltitude(0);
//     socketc.on('alt1', function(data) {
//         console.log('Received altitude 2 update:', data.data);
//         const altitudeInFeet = data.data * 3.28084;
//         altimeter2.setAltitude(altitudeInFeet);
//         document.querySelector("#altitude2_dis").innerHTML="Altitude : "+data.data+" m";
//     });
    
// })


// $(document).ready(function() {
//     var heading2 = $.flightIndicator('#heading2', 'heading');
//     heading2.setHeading(0);
//     socketc.on('yaw1', function(data) {
//         heading2.setHeading(data.data);
//         document.querySelector("#heading2_dis").innerHTML="YAW : "+data.data;
//     });
    
// })
const socketc = io("http://192.168.2.101:5500");
socketc.on('connect',function(){
    console.log(`connected with socket ID 1 : ${socketc.id}`);
});

$(document).ready(function() {
    var altimeter2 = $.flightIndicator('#altimeter2', 'altimeter');
    // altimeter2.setAltitude(0);
    socketc.on('alt1', function(data) {
        console.log('Received altitude 2 update:', data.data);
        const altitudeInFeet = data.data * 3.28084;
        altimeter2.setAltitude(altitudeInFeet);
        document.querySelector("#altitude2_dis").innerHTML="Altitude : "+data.data+" m";
    });
    
})


$(document).ready(function() {
    var heading2 = $.flightIndicator('#heading2', 'heading');
    // heading2.setHeading(0);
    socketc.on('yaw1', function(data) {
        heading2.setHeading(data.data);
        document.querySelector("#heading2_dis").innerHTML="YAW : "+data.data;
    });
    
})









$(document).ready(function() {
    $("#demo1").gauge(0, {
        min: 0,
        max: 100,
        unit: " Mpbs",
        color: "red",
        colorAlpha: 1,
        bgcolor: "#222",
        type: "default"
    });

    $("#demo2").gauge(0, {
        min: 0,
        max: 100,
        unit: " Mpbs",
        color: "green",
        colorAlpha: 1,
        bgcolor: "#222",
        type: "default"
    });
});




