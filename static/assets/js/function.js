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
            
            console.log("Add to cart button clicked");
            
            let this_val = $(this);
            let product_id = this_val.attr("data-index");
            console.log("Product ID:", product_id);
            
            let quantity = $(".product-quantity-" + product_id).val() || 1;
            let product_title = $(".product-title-" + product_id).val();
            
            // Get product price - with multiple fallback options
            let product_price;
            
            // Try multiple ways to get the product price in order of specificity
            // First check for the ID which is unique
            if ($("#current-product-price").length > 0) {
                product_price = $("#current-product-price").text().trim();
                console.log("Found price using #current-product-price:", product_price);
            }
            // Try the class specifically for this product ID 
            else if ($(".current-product-price-" + product_id).length > 0) {
                product_price = $(".current-product-price-" + product_id).text().trim();
                console.log("Found price using class with ID:", product_price);
            }
            // Try the generic class
            else if ($(".current-product-price").length > 0) {
                product_price = $(".current-product-price").text().trim();
                console.log("Found price using generic class:", product_price);
            }
            // If all else fails, check for any price related element
            else {
                product_price = $(".price").text().trim();
                console.log("Found price using .price class:", product_price);
            }
            
            // If we still don't have a price, set a default to prevent errors (can be fixed later by admin)
            if (!product_price) {
                console.error("Could not find price, using default price of 0");
                product_price = "0";
            }
            
            // Clean the price - remove currency symbol if present
            product_price = product_price.replace(/[$£€]/g, '').trim();
            
            console.log("Quantity:", quantity);
            console.log("Title:", product_title);
            console.log("Final Price being used:", product_price);
            
            let product_pid = $(".product-pid-" + product_id).val();
            
            // Get product image with multiple fallbacks
            let product_image;
            
            if ($(".product-image-" + product_pid).length > 0) {
                product_image = $(".product-image-" + product_pid).val();
            } else if ($(".product-image-" + product_id).length > 0) {
                product_image = $(".product-image-" + product_id).val();
            } else if ($(".product-image-slider img:first").length > 0) {
                product_image = $(".product-image-slider img:first").attr("src");
            } else if ($(".product-img img:first").length > 0) {
                product_image = $(".product-img img:first").attr("src");
            } else {
                // Default placeholder image if nothing else works
                product_image = "/static/assets/imgs/shop/product-1-1.jpg";
            }
            
            console.log("PID:", product_pid);
            console.log("Image:", product_image);

            console.log("Adding to cart:", {
                id: product_id,
                title: product_title,
                price: product_price,
                qty: quantity,
                pid: product_pid,
                image: product_image
            });

            $.ajax({
                url: window.location.origin + '/add-to-cart/',
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
                    console.log("Sending Ajax request");
                    this_val.prop('disabled', true);
                },
                success: function(response){
                    console.log("Success response:", response);
                    this_val.html("Added to cart");
                    $(".cart-items-count").text(response.totalcartitems);
                    setTimeout(function(){
                        this_val.prop('disabled', false);
                        this_val.html('<i class="fi-rs-shopping-cart mr-5"></i>Add');
                    }, 2000);
                },
                error: function(xhr, status, error) {
                    console.error("Error adding to cart:", error);
                    console.error("Status:", status);
                    console.error("Response:", xhr.responseText);
                    this_val.prop('disabled', false);
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
                    console.log("Delete response:", response);
                    this_val.css('opacity', '1');
                    row.fadeOut(400, function() {
                        row.remove();
                        $(".cart-items-count").text(response.totalcartitems);
                        
                        // Update the cart summary section
                        let cartSummary = `
                            <div class="d-flex justify-content-between mb-2">
                                <p class="fw-bold">Tax</p>
                                <p>$0.00</p>
                            </div>
                            <div class="d-flex justify-content-between mb-2">
                                <p class="fw-bold">Shipping</p>
                                <p>$0.00</p>
                            </div>
                            <div class="d-flex justify-content-between mb-2">
                                <p class="fw-bold">Discount</p>
                                <p>$0.00</p>
                            </div>
                            <div class="d-flex justify-content-between mb-2">
                                <p class="fw-bold">Total</p>
                                <p>$${parseFloat(response.cart_total_amount).toFixed(2)}</p>
                            </div>
                        `;
                        $(".cart-totals .table-responsive div").html(cartSummary);
                        
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
                    console.log("Update response:", response);
                    this_val.css('opacity', '1');
                    
                    // Update the cart item count
                    $(".cart-items-count").text(response.totalcartitems);
                    
                    // Update the subtotal for this row
                    row.find('.text-brand').text('$' + parseFloat(response.item_total).toFixed(2));
                    
                    // Update the cart summary section
                    let cartSummary = `
                        <div class="d-flex justify-content-between mb-2">
                            <p class="fw-bold">Tax</p>
                            <p>$0.00</p>
                        </div>
                        <div class="d-flex justify-content-between mb-2">
                            <p class="fw-bold">Shipping</p>
                            <p>$0.00</p>
                        </div>
                        <div class="d-flex justify-content-between mb-2">
                            <p class="fw-bold">Discount</p>
                            <p>$0.00</p>
                        </div>
                        <div class="d-flex justify-content-between mb-2">
                            <p class="fw-bold">Total</p>
                            <p>$${parseFloat(response.cart_total_amount).toFixed(2)}</p>
                        </div>
                    `;
                    $(".cart-totals .table-responsive div").html(cartSummary);
                    
                    // If cart is empty, reload the page
                    if (response.totalcartitems === 0) {
                        location.reload();
                    }
                },
                error: function(xhr, status, error){
                    this_val.css('opacity', '1');
                    console.error("Error updating cart:", error);
                    console.error("Status:", status);
                    console.error("Response:", xhr.responseText);
                }
            });
        });


        
    })

    // Javascript to allow user to make address default in their dashboard
    $(document).on("click", ".make-default-address", function () {
        let id = $(this).attr("data-address-id")
        let this_val = $(this)

        $.ajax({
            url: "/make-default-address/",
            data: {
                "id": id
            },
            dataType: "json",
            success: function (response) {
                if (response.boolean == true) {
                    $(".check").hide()
                    $(".action_btn").show()
                    
                    $(".check" + id).show()
                    $(".button" + id).hide()
                }
            }
        })
    })

    // Javascript to allow user to add items into their wishlist
    $(document).on("click", ".add-to-wishlist", function () {
        let product_id = $(this).attr("data-product-item")
        let this_val = $(this)


        console.log("PRoduct ID IS", product_id);

        $.ajax({
            url: "/add-to-wishlist/",
            data: {
                "id": product_id
            },
            dataType: "json",
            beforeSend: function () {
                console.log("Adding to wishlist...")
            },
            success: function (response) {
                
                this_val.html("<i class='fas fa-heart text-danger'></i>")
                if (response.bool === true) {
                    console.log("Added to wishlist...");
                }
            }
        })
    })

    // We can't forget about REMOVING products from wishlist 
    // Javascript below is feature to remove from wishlist
    $(document).on("click", ".delete-wishlist-product", function () {
        let wishlist_id = $(this).attr("data-wishlist-product")
        let this_val = $(this)

        console.log("wishlist id is:", wishlist_id);

        $.ajax({
            url: "/remove-from-wishlist/",
            data: {
                "id": wishlist_id
            },
            dataType: "json",
            beforeSend: function () {
                console.log("Deleting product from wishlist...");
            },
            success: function (response) {
                $("#wishlist-list").html(response.data)
            },
            error: function(xhr, status, error) {
                console.error("Error removing from wishlist:", error);
                console.log(xhr.responseText);
            }
        })
    })


    $(document).on("submit", "#contact-form-ajax", function (e) {
        e.preventDefault()
        console.log("Submited...");

        let full_name = $("#full_name").val()
        let email = $("#email").val()
        let phone = $("#phone").val()
        let subject = $("#subject").val()
        let message = $("#message").val()
        let csrftoken = $('input[name="csrfmiddlewaretoken"]').val()

        console.log("Name:", full_name);
        console.log("Email:", email);
        console.log("Phone:", phone);
        console.log("Subject:", subject);
        console.log("Message:", message);

        $.ajax({
            url: "/ajax-contact-form/",
            data: {
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "subject": subject,
                "message": message,
                "csrfmiddlewaretoken": csrftoken
            },
            type: "POST",
            dataType: "json",
            beforeSend: function () {
                console.log("Sending Data to Server...");
            },
            success: function (res) {
                console.log("Sent Data to server!");
                $(".contact_us_p").hide()
                $("#contact-form-ajax").hide()
                $("#message-response").html("Message sent successfully.")
            },
            error: function(xhr, status, error) {
                console.error("Error sending message:", error);
                console.log("Status:", status);
                console.log("Response:", xhr.responseText);
                $("#message-response").html("Error sending message. Please try again.").css("color", "red");
            }
        })
    })

    // Vendor Application Form
    $(document).on("submit", "#vendor-application-form", function (e) {
        e.preventDefault()
        console.log("Vendor Application Submitted...");

        // Create FormData object to handle file uploads
        let formData = new FormData(this);
        
        $.ajax({
            url: "/vendor-application-form/",
            data: formData,
            type: "POST",
            dataType: "json",
            processData: false,
            contentType: false,
            beforeSend: function () {
                console.log("Sending Application Data to Server...");
                $("#vendor-form-btn").text("Submitting...").prop("disabled", true);
            },
            success: function (res) {
                console.log("Sent Application Data to server!");
                $(".vendor_app_p").hide()
                $("#vendor-application-form").hide()
                $("#message-response").html(res.data.message)
                $("#vendor-form-btn").text("Submit Application").prop("disabled", false);
            },
            error: function(xhr, status, error) {
                console.error("Error submitting application:", error);
                console.log("Status:", status);
                console.log("Response:", xhr.responseText);
                $("#message-response").html("Error submitting application. Please try again.").css("color", "red");
                $("#vendor-form-btn").text("Submit Application").prop("disabled", false);
            }
        })
    })

}
