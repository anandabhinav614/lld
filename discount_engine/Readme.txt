Design a Shopping Coupon & Discount Management System for an e-commerce platform.

The system should support: 
1. Products have: id name price
2. Customer can add products to cart.
3. Multiple coupon types should be supported: Flat Discount, Percentage Discount,
Percentage Discount With Cap
4. Only one coupon can be applied at a time.
5. Coupon should validate itself before applying.


ER:
    Product

    Cart

    Coupon (abstract)

    FlatCoupon
    PercentageCoupon
    PercentageWithCapCoupon

    CouponService (or CheckoutService)