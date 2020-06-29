const cameraSelection = document.getElementById('cameraSelection');
$(document).ready(function() {
    Html5Qrcode.getCameras().then(cameras => {
        /**
         * devices would be an array of objects of type:
         * { id: "id", label: "label" }
         */
        if (cameras && cameras.length) {
            for (var i = 0; i < cameras.length; i++) {
                const camera = cameras[i];
                const value = camera.id;
                const name = camera.label == null ? value : camera.label;
                const option = document.createElement('option');
                option.value = value;
                option.innerHTML = name;
                cameraSelection.appendChild(option);
            }
        }
        if (cameras && cameras.length) {
            var cameraId = cameras[0].id;
            // .. use this to start scanning.

            const html5QrCode = new Html5Qrcode("qr");
            html5QrCode.start(
                cameraId, // retreived in the previous step.
                {
                    fps: 10, // sets the framerate to 10 frame per second
                    qrbox: 250 // sets only 250 X 250 region of viewfinder to
                    // scannable, rest shaded.
                },
                qrCodeMessage => {
                    // do something when code is read. For example:
                    console.log(`QR Code detected: ${qrCodeMessage}`);
                    window.location.replace(qrCodeMessage)
                    html5QrCode.stop().then(ignore => {
                        // QR Code scanning is stopped.
                        // console.log("QR Code scanning stopped.");
                    }).catch(err => {
                        // Stop failed, handle it.
                        // console.log("Unable to stop scanning.");
                    });
                },
                errorMessage => {
                    // parse error, ideally ignore it. For example:
                    // console.log(`QR Code no longer in front of camera.`);
                })
            .catch(err => {
                // Start failed, handle it. For example,
                // console.log(`Unable to start scanning, error: ${err}`);
            });
        }
    }).catch(err => {
        console.log(err)
    });
})

$('#cameraSelection').change(function(){
    var cameraId = cameraSelection.value;
    // .. use this to start scanning.

    const html5QrCode = new Html5Qrcode("qr");
    html5QrCode.start(
        cameraId, // retreived in the previous step.
        {
            fps: 10, // sets the framerate to 10 frame per second
            qrbox: 250 // sets only 250 X 250 region of viewfinder to
            // scannable, rest shaded.
        },
        qrCodeMessage => {
            // do something when code is read. For example:
            console.log(`QR Code detected: ${qrCodeMessage}`);
            window.location.replace(qrCodeMessage)
            html5QrCode.stop().then(ignore => {
                // QR Code scanning is stopped.
                // console.log("QR Code scanning stopped.");
            }).catch(err => {
                // Stop failed, handle it.
                // console.log("Unable to stop scanning.");
            });
        },
        errorMessage => {
            // parse error, ideally ignore it. For example:
            // console.log(`QR Code no longer in front of camera.`);
        })
    .catch(err => {
        // Start failed, handle it. For example,
        // console.log(`Unable to start scanning, error: ${err}`);
    });
})