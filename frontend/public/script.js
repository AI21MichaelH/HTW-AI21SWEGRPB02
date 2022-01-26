// Elements for taking the snapshot
var canvas;
var context;
var input;
var video;
var baseURL = "http://localhost:5000/file/";
var dataURL;

function load(){
    // Grab elements, create settings, etc.
    video = document.getElementById('video');

    // Get access to the camera!
    if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        // Not adding `{ audio: true }` since we only want video now
        navigator.mediaDevices.getUserMedia({ video: true }).then(function(stream) {
            //video.src = window.URL.createObjectURL(stream);
            video.srcObject = stream;
            video.play();
        });
    }

    // testing call to frontend server
    var frontendServerURL = 'http://localhost:3000';
    const url = frontendServerURL + '/messages';
    fetch(url, {
            method: 'POST',
            body: 'Testing a message!',
            headers: {
                'Content-Type': 'text/plain'
            }
        })
        .then(response => {})
        .catch(err => {
            console.log('ERROR:', err);
        });
}

// Trigger photo take
function snap() {
    canvas = document.getElementById('canvas');
    context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, 640, 480);

    dataURL = canvas.toDataURL('image/jpeg');
    console.log(dataURL);
}

//Trigger on submit
function submit(){
    input = document.getElementById("fname").value;

    const url = baseURL + input;
    console.log(url);
    fetch(url, {
            method: 'POST',
            body: dataURL,
            headers: {
                'Content-Type': 'text/plain'
            }
        })
        .then(response => response.json())
         .then(data => { 
            console.log(data);
    });
}

function saveName(){
    input = document.getElementById("fname").value;
    window.sessionStorage.setItem('input', input);
    console.log(window.sessionStorage.getItem('input'));
}

function showVideo(){
    input = window.sessionStorage.getItem('input');
    console.log(input);

    if(input == null || input == ""){
        document.getElementById("error").innerHTML = "Please enter a name!";
    }
    else{
        var video2 = document.getElementById('video');
        var source = document.createElement('source');

        source.setAttribute('src', baseURL + 'video/' + input);
        source.setAttribute('type', 'video/mp4');

        video2.appendChild(source);
        video2.play();
        console.log({
            src: source.getAttribute('src'),
            type: source.getAttribute('type'),
        });
    }
}
