function updatedata(){
var data =JSON.parse(localStorage.getItem('data'));
 $.post("https://9e09d632.ngrok.io/dashboard",data.user_info,function(str){
                    localStorage.clear()
     
                   localStorage.setItem('data', JSON.stringify(str)); 
                    var jsondata = JSON.parse(localStorage.getItem('data'));
            

            
            
             document.getElementById("dashboard-product-div").innerHTML =`
                    ${jsondata.products_info.map(populateProduct).join(" ")}`
      
                });
}

function colorCard(product){
                if(product.price_init > product.price_update)
                    {
                        return `success`
                    }
                else if(product.price_init == product.price_update)
                    {
                        return `info`
                    }
                else
                    {
                        return `danger`
                    }
            }
function populateProduct(product){
                 return `
                        <div class="col-md-4 stretch-card grid-margin">
                            <div class="card bg-gradient-${colorCard(product)} card-img-holder text-white">
                                <div class="card-body">
                                    <img src="assets/images/dashboard/circle.svg" class="card-img-absolute" alt="circle-image" />
                                        <h2 class="font-weight-normal mb-3">${product.product_id}
                                     </h2>
                                    <h4 class="mb-5">${product.price_update}</h4>
                                  </div>
                                </div>
                              </div>`
            }