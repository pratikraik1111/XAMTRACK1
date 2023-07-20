"use strict";

$("#buttonid").click(function(){
            var form=$("#formid").serialize();
           
             $.post("https://9e09d632.ngrok.io/login",form,function(str){
 
                // json data
                

                console.log(str)
                if (str.success == 1){
                    
                localStorage.clear();
                window.location.replace("./dashboard/index.html");
                
                localStorage.setItem('data', JSON.stringify(str));    
                    
               
                    
                }
                 
                else{
                     alert(str);
                }
                
            })
        });


//str = {  "user_info" : {userid: 35, username: "asdf"},
//                     "products_info" : [{
//                         product_img : "https://images-na.ssl-images-amazon.com/images/I/61DWjP%2BP6XL._SX679_.jpg",
//                         aff_url: "https://www.amazon.in/Lipton-Pure-Light-Green-Piec…1_3?srs=21246951031&ie=UTF8&qid=1586463241&sr=8-3", price_init: 423, price_update: 423, product_id: 1},
//                                       {    
//                                           product_img : "https://images-na.ssl-images-amazon.com/images/I/61DWjP%2BP6XL._SX679_.jpg",
//                                           price_init : 5800,
//                                           price_update: 5000,
//                                           product_id: 2
//                                       },
//                                       {   product_img : "https://images-na.ssl-images-amazon.com/images/I/61DWjP%2BP6XL._SX679_.jpg",
//                                           price_init : 15000,
//                                           price_update: 16000,
//                                           product_id: 2
//                                       },]
//                 }


