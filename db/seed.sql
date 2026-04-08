INSERT INTO eerm_users (
    user_name, user_email, user_pass, user_role,
    dept_id, user_status, user_contact, user_address,
    user_about, user_img_url, created_at
)
SELECT * FROM (
    SELECT 
        'Admin',
        'admin@gmail.com',
        'scrypt:32768:8:1$rM5KgHdf0D9ka27f$77598cb2abb34e00629f259652e81a143a79e841d3850605cefc24cbbbca08845f9c3cc8298d10d971daf56a10dbca213223fd5c300604cb50870fdd7e18b8ff',
        'Admin',
        NULL,
        'Active',
        NULL,
        NULL,
        'System Administrator',
        NULL,
        NOW()
) AS tmp
WHERE NOT EXISTS (
    SELECT user_email FROM eerm_users WHERE user_email = 'admin@gmail.com'
);