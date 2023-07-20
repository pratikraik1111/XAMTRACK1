const video = document.getElementById('video')

Promise.all([
  faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
  faceapi.nets.faceLandmark68Net.loadFromUri('/models'),
  faceapi.nets.faceRecognitionNet.loadFromUri('/models'),
  
]).then(startVideo)

function startVideo() {
  navigator.getUserMedia(
    { video: {} },
    stream => video.srcObject = stream,
    err => console.error(err)
  )
}
var c=0;
var k=0;
video.addEventListener('playing', () => {
  const canvas = faceapi.createCanvasFromMedia(video)
  document.body.append(canvas)
  const displaySize = { width: video.width, height: video.height }
  faceapi.matchDimensions(canvas, displaySize)
  setInterval(async () => {
    const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks()
    const facesCount = detections.length
    if(facesCount!=1)
      {
                   k++;          
                   
                               //if there is no detections
    }
   
   else{ 
    k=0;
    // const resizedDetections = faceapi.resizeResults(detections, displaySize)
    // canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)
    // faceapi.draw.drawDetections(canvas, resizedDetections)
    // faceapi.draw.drawFaceLandmarks(canvas, resizedDetections)
    const numRows = 4;
    const modelPoints = cv.matFromArray(numRows, 3, cv.CV_64FC1, [
      0.0,
      0.0,
      0.0, // Nose tip
      0.0,
      0.0,
      0.0, // HACK! solvePnP doesn't work with 3 points, so copied the
      //   first point to make the input 4 points
      // 0.0, -330.0, -65.0,  // Chin
      -225.0,
      170.0,
      -135.0, // Left eye left corner
      225.0,
      170.0,
      -135.0 // Right eye right corne
      // -150.0, -150.0, -125.0,  // Left Mouth corner
      // 150.0, -150.0, -125.0,  // Right mouth corner
    ]);

    // Camera internals
  const size = { width: 640, height: 480 };
  const focalLength = size.width;
  const center = [size.width / 2, size.height / 2];
  const cameraMatrix = cv.matFromArray(3, 3, cv.CV_64FC1, [
    focalLength,
    0,
    center[0],
    0,
    focalLength,
    center[1],
    0,
    0,
    1
  ]);
  console.log("Camera Matrix:", cameraMatrix.data64F);
    // Create Matrixes
    const imagePoints = cv.Mat.zeros(numRows, 2, cv.CV_64FC1);
    const distCoeffs = cv.Mat.zeros(4, 1, cv.CV_64FC1); // Assuming no lens distortion
    const rvec = new cv.Mat({ width: 1, height: 3 }, cv.CV_64FC1);
    const tvec = new cv.Mat({ width: 1, height: 3 }, cv.CV_64FC1);
    const pointZ = cv.matFromArray(1, 3, cv.CV_64FC1, [0.0, 0.0, 500.0]);
    const pointY = cv.matFromArray(1, 3, cv.CV_64FC1, [0.0, 500.0, 0.0]);
    const pointX = cv.matFromArray(1, 3, cv.CV_64FC1, [500.0, 0.0, 0.0]);
    const noseEndPoint2DZ = new cv.Mat();
    const nose_end_point2DY = new cv.Mat();
    const nose_end_point2DX = new cv.Mat();
    const jaco = new cv.Mat();
    window.beforeunload = () => {
      im.delete();
      imagePoints.delete();
      distCoeffs.delete();
      rvec.delete();
      tvec.delete();
      pointZ.delete();
      pointY.delete();
      pointX.delete();
      noseEndPoint2DZ.delete();
      nose_end_point2DY.delete();
      nose_end_point2DX.delete();
      jaco.delete();
    };

    const ns = detections[0]['landmarks']['positions'][33];
    const le = detections[0]['landmarks']['positions'][45];
    const re = detections[0]['landmarks']['positions'][36];

      [
        ns.x,
        ns.y, // Nose tip
        ns.x,
        ns.y, // Nose tip (see HACK! above)
        // 399, 561, // Chin
        le.x,
        le.y, // Left eye left corner
        re.x,
        re.y // Right eye right corner
        // 345, 465, // Left Mouth corner
        // 453, 469 // Right mouth corner
      ].map((v, i) => {
        imagePoints.data64F[i] = v;
      });
      tvec.data64F[0] = -100;
      tvec.data64F[1] = 100;
      tvec.data64F[2] = 1000;
           const distToLeftEyeX = Math.abs(le.x - ns.x);
           const distToRightEyeX = Math.abs(re.x - ns.x);
      if (distToLeftEyeX < distToRightEyeX) {
        // looking at left
        rvec.data64F[0] = -1.0;
        rvec.data64F[1] = -0.75;
        rvec.data64F[2] = -3.0;
      } else {
        // looking at right
        rvec.data64F[0] = 1.0;
        rvec.data64F[1] = -0.75;
        rvec.data64F[2] = -3.0;
      }

      const success = cv.solvePnP(
        modelPoints,
        imagePoints,
        cameraMatrix,
        distCoeffs,
        rvec,
        tvec,
        true
      );
      if (!success) {
        return;
      }
                               
         

     
                                    //if detection is found
      if(((rvec.data64F[0])/Math.PI)*180 <-62 || ((rvec.data64F[0])/Math.PI)*180 >77)
      {
        c++; 
        console.log("be steady and look straight");
        if(c==10)
        {
        
          alert("Stop peeping");
          c=0;
  
        }
      }
      else
      c=0;

     
    

      // Project a 3D points [0.0, 0.0, 500.0],  [0.0, 500.0, 0.0],
      //   [500.0, 0.0, 0.0] as z, y, x axis in red, green, blue color
      cv.projectPoints(
        pointZ,
        rvec,
        tvec,
        cameraMatrix,
        distCoeffs,
        noseEndPoint2DZ,
        jaco
      );
      cv.projectPoints(
        pointY,
        rvec,
        tvec,
        cameraMatrix,
        distCoeffs,
        nose_end_point2DY,
        jaco
      );
      cv.projectPoints(
        pointX,
        rvec,
        tvec,
        cameraMatrix,
        distCoeffs,
        nose_end_point2DX,
        jaco
      );

      // let im = cv.imread(document.querySelector("canvas"));
      // // color the detected eyes and nose to purple
      // for (var i = 0; i < numRows; i++) {
      //   cv.circle(
      //     im,
      //     {
      //       x: imagePoints.doublePtr(i, 0)[0]+47,
      //       y: imagePoints.doublePtr(i, 1)[0]+40
      //     },
      //     3,
      //     [255, 0, 255, 255],
      //     -1
      //   );
      // }
      // // draw axis
      // const pNose = { x: imagePoints.data64F[0]+47, y: imagePoints.data64F[1]+40 };
      // const pZ = {
      //   x: noseEndPoint2DZ.data64F[0]+47,
      //   y: noseEndPoint2DZ.data64F[1]+40
      // };
      // const p3 = {
      //   x: nose_end_point2DY.data64F[0]+47,
      //   y: nose_end_point2DY.data64F[1]+40
      // };
      // const p4 = {
      //   x: nose_end_point2DX.data64F[0]+47,
      //   y: nose_end_point2DX.data64F[1]+40
      // };
      // cv.line(im, pNose, pZ, [255, 0, 0, 255], 2);
      // cv.line(im, pNose, p3, [0, 255, 0, 255], 2);
      // cv.line(im, pNose, p4, [0, 0, 255, 255], 2);
    
      // cv.imshow(document.querySelector("canvas"), im);
      // im.delete();
    }
    if(k>=15)
    {
    alert("Don't hide..!"); 
    k=0;                       // if continuousely in 15 frames, no detections are found
    }
    
      
  }, 200)
})