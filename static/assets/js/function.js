// Check if jQuery is loaded
if (typeof jQuery === 'undefined') {
    console.error('jQuery is not loaded. Please check your script includes.');
} else {
    console.log("function.js loaded successfully");

    const monthNames = ['January', 'February', 'March', 'April' ,'May' ,'June' ,'July', 'August', 'September', 'October', 'November', 'December']

    $("#commentForm").submit(function(e){
        e.preventDefault();

        let dt = new Date();
        let time = dt.getDate() + " "+ monthNames[dt.getUTCMonth()] + ", " + dt.getFullYear()

        $.ajax({
            data: $(this).serialize(),

            method: $(this).attr("method"),
            url: $(this).attr("action"),
            dataType: "json", 

            success: function(response){
                console.log("Comment Saved to Database")
                
                //responsible for hiding review form after user submits it 
                if(response.bool == true){
                    $("#review-response").html("Review Added!")
                    $(".hide-comment-form").hide()
                    $(".add-review").hide()

                    let _html = '<div class="single-comment justify-content-between d-flex mb-30">'
                        _html += '<div class="thumb text-center">'
                        _html +='<img src="/static/assets/imgs/blog/author-2.png" alt="" />'
                        _html +='<a href="#" class="font-heading text-brand">' + response.context.user + '</a>'
                        _html +='</div>'

                        _html += '<div class="desc">'
                        _html +='<div class="d-flex justify-content-between mb-10">'
                        _html +='<div class="d-flex align-items-center">'
                        _html +='<span class="font-xs text-muted"> '+ time +' </span>'
                        _html +='</div>'

                        for(let i = 1; i <= response.context.rating; i++ ) {
                            _html += '<i class = "fas fa-star text-warning"></i>'
                        }
                        
                        _html +='</div>'
                        _html +='<p class="mb-10"> ' + response.context.review +' </p>'
                        _html +='</div>'
                        _html +='</div>'
                        _html +='</div>'

                        $(".comment-list").prepend(_html)
                }

            }

        })
    })


    // Whenever a user clicks on a checkbox 
    $(document).ready(function(){
        
        $(".filter-checkbox, #price-filter-btn").on("click", function(){
            console.log("A checkbox has been clicked")

            let filter_object = {}

            // its going to views.py to get "max_price"
            let min_price = $("#max_price").attr("min")
            let max_price = $("#max_price").val()

            filter_object.min_price = min_price;
            filter_object.max_price = max_price;


            $(".filter-checkbox").each(function(){
                let filter_value = $(this).val()
                let filter_key = $(this).data("filter")

                filter_object[filter_key] = Array.from(document.querySelectorAll('input[data-filter=' + filter_key + ']:checked')).map(function(element){
                    return element.value
                })
            })
            console.log("Filter Object is: ", filter_object)
            $.ajax({
                url: '/filter-products',
                data: filter_object,
                dataType: 'json',
                beforeSend: function(){
                    console.log("Sending Data")
                },
                success:function(response){
                    console.log(response);
                    console.log("Data filter successfully!")
                    $("#filtered-proudct").html(response.data)
                }
            })
        })

        $("#max_price").on("blur", function(){
            let min_price = $(this).attr("min")
            let max_price = $(this).attr("max")
            let current_price = $(this).val()
        
            if (current_price < parseInt(min_price) || current_price > parseInt(max_price)) { 
                min_price = Math.round(min_price * 100)/100
                max_price = Math.round(max_price * 100)/100
        
                alert("Price must be between $"+min_price + ' and $'+max_price)
                $(this).val(min_price)
                $("#range").val(min_price)
                $(this).focus()
                return false
            }
        })

        // Add to cart functionality
        $(document).on("click", ".add-to-cart-btn", function(e){
            e.preventDefault();
            
            let this_val = $(this);
            let product_id = this_val.attr("data-index");
            let quantity = $(".product-quantity-" + product_id).val() || 1;
            let product_title = $(".product-title-" + product_id).val();
            // Get price from the closest product card
            let product_price = this_val.closest('.product-cart-wrap').find('.current-product-price').text().replace('$', '').trim();
            let product_pid = $(".product-pid-" + product_id).val();
            let product_image = $(".product-image-" + product_pid).val();

            console.log("Adding to cart:", {
                id: product_id,
                title: product_title,
                price: product_price,
                qty: quantity,
                pid: product_pid,
                image: product_image
            });

            $.ajax({
                url: '/add-to-cart/',
                data: {
                    'id': product_id,
                    'title': product_title,
                    'qty': quantity,
                    'price': product_price,
                    'pid': product_pid,
                    'image': product_image
                },
                dataType: 'json',
                beforeSend: function(){
                    this_val.prop('disabled', true);
                },
                success: function(response){
                    this_val.html("Added to cart");
                    $(".cart-items-count").text(response.totalcartitems);
                    setTimeout(function(){
                        this_val.prop('disabled', false);
                        this_val.html('<i class="fi-rs-shopping-cart mr-5"></i>Add');
                    }, 2000);
                }
            });
        });

        // Delete from cart
        $(document).on("click", ".delete-product", function(){
            let product_id = $(this).attr("data-product");
            let this_val = $(this);
            let row = this_val.closest('tr');

            $.ajax({
                url: '/delete-from-cart/',
                data: {
                    "id": product_id
                },
                dataType: 'json',
                beforeSend: function(){
                    this_val.css('opacity', '0.5');
                },
                success: function(response){
                    this_val.css('opacity', '1');
                    row.fadeOut(400, function() {
                        row.remove();
                        $(".cart-items-count").text(response.totalcartitems);
                        $(".cart_total_amount").text("$" + response.cart_total_amount);
                        if (response.totalcartitems === 0) {
                            location.reload();
                        }
                    });
                }
            });
        });

        // Update cart
        $(document).on("click", ".update-product", function(){
            let this_val = $(this);
            let product_id = this_val.attr("data-product");
            let product_quantity = $(".product-qty-" + product_id).val();
            let row = this_val.closest('tr');

            $.ajax({
                url: '/update-cart/',
                data: {
                    "id": product_id,
                    "qty": product_quantity
                },
                dataType: 'json',
                beforeSend: function(){
                    this_val.css('opacity', '0.5');
                },
                success: function(response){
                    this_val.css('opacity', '1');
                    
                    // Update the cart item count
                    $(".cart-items-count").text(response.totalcartitems);
                    
                    // Update the subtotal for this row
                    row.find('.text-brand').text('$' + response.item_total);
                    
                    // Update the cart total amount
                    $(".cart_total_amount").text('$' + response.cart_total_amount);
                    
                    // If cart is empty, reload the page
                    if (response.totalcartitems === 0) {
                        location.reload();
                    }
                },
                error: function(){
                    this_val.css('opacity', '1');
                    console.error("Error updating cart");
                }
            });
        });
    })

    // Responsible to tell user whether the price is possible or not 
    // Let me explain: If the minimum price on the entire shop is $2 and the user filters 
    // looking for a product for $1, they will be prompted a message on their browser telling them 
    // the range of prices for the filter slider to work


    // Cart functionality
    // Whenever the user clicks on the quantity field we're going to grab
    // the product id and the name of the product 


    /////////// THIS IS THE OLD ADD TO CART BUTTON /////////

    // $("#add-to-cart-btn").on("click", function(){
    //     let quantity = $("#product-quantity").val()
    //     let product_title = $(".product-title").val()
    //     let product_id = $(".product-id").val()
    //     // in product-detail.hmtl the price we see is a text field not val
    //     let product_price = $("#current-product-price").text()

    //     console.log("Quantity: ", quantity);
    //     console.log("Title: ", product_title);
    //     console.log("Price: ", product_price);
    //     console.log("ID: ", product_id);
    //     console.log("Current Element: ", this_val);

    //     $.ajax({
    //         url: 'add-to-cart',
    //         data:{
    //             'id': product_id, 
    //             'quantity': quantity,
    //             'title':product_title,
    //             'price':product_price,

    //         },
    //         dataType: 'json',
    //         beforeSend: function(response){
    //             console.log("Adding Products to Cart...");
    //         },
    //         sucess:function(response){
    //             this_val.html("Successfully Added Products to Cart")
    //             console.log("Successfully Added Products to Cart");
    //             $(".cart-items-count").text(response.totalcartitems)
    //         }
    //     })
    // })

    ///////////////// NEW ADD TO CART BUTTON ///////////////
}
