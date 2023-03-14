$('#slider1, #slider2, #slider3').owlCarousel({
    loop: true,
    margin: 20,
    responsiveClass: true,
    responsive: {
        0: {
            items: 1,
            nav: false,
            autoplay: true,
        },
        600: {
            items: 3,
            nav: true,
            autoplay: true,
        },
        1000: {
            items: 5,
            nav: true,
            loop: true,
            autoplay: true,
        }
    }
})

$(document).ready(function() {

    $('.plus-cart').click(function(){
        var id = $(this).attr("pid").toString();
        var eml = this.parentNode.children[2]
        $.ajax({
            type:"GET",
            url:"pluscart",
            data:{
                prod_id : id
            },
            success: function (data) {
                eml.innerText = data.quantity;
                document.getElementById("amount").innerText = data.amount;
                document.getElementById("totalamount").innerText = data.totalamount;
            }
        })
    })

    $('.minus-cart').click(function(){
        var id = $(this).attr("pid").toString();
        var eml = this.parentNode.children[2]
        var emll = this
        $.ajax({
            type:"GET",
            url:"minuscart",
            data:{
                prod_id : id
            },
            success: function (data) {
            
                var q = data.quantity;
                if (q == 0) {
                    eml.parentNode.parentNode.parentNode.parentNode.remove();
                    location.reload();
                } else {
                    $(eml).text(data.quantity);
                    $("#amount").text(data.amount);
                    $("#totalamount").text(data.totalamount);
                }
            }
        })
    })

    $('.remove-cart').click(function(){
        var id = $(this).attr("pid").toString();
        var eml = this
        $.ajax({
            type:"GET",
            url:"removecart",
            data:{
                prod_id : id
            },
            success: function (data) {
                $("#amount").text(data.amount);
                $("#totalamount").text(data.totalamount);
                eml.parentNode.parentNode.parentNode.parentNode.remove()
                location.reload();
            }
        })
    })


    $('.delete-address').click(function() {
        var address_id = $(this).attr("address-id").toString();
        var card = $(this).closest('.card');
        $.ajax({
            type: "GET",
            url: "delete_address",
            data:{
                address_id : address_id
            },
            success: function(data) {
                card.parent().remove(); // remove the parent container of the card (i.e. the col-sm-6 container)
                location.reload(); // reload the page
            }
        });
    });
    

    
});





// function ajax_send_otp(){
//    phone = document.getElementById("phone");
//  $.GET("/send_otp",
//     {
//         "phone":phone,
//         "csrfmiddlewaretoken":"{{csrf_token}}"
//     },
//         );
// }

