var jsondata = JSON.parse(localStorage.getItem('data'));
if (jsondata.success == 1){
     window.location.replace("./dashboard/index.html");
}