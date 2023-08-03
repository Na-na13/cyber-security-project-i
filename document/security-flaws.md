**Credential stuffing**  
https://github.com/jazzband/django-axes
-	No limits on how many times user can attempt to login. Attacker may use the application for e.g. testing username-password -pairs or dictionary attack
-	How to fix:    
    -	Django axes  
        - if user has 3 unsuccessful login attempts, the account is locked for defined period of time (3 minutes at the moment for test reasons)
        -	compares username + IP-address combination to prevent denial of service attacks (if done only based on username, increases possibility of DoS attack) 
  
**Cross-Site Request Forgery (CSRF)**
-	User can be tricked to visit malicious webpage which contains broken image. When browser loads the page, spam-message is sent to every user of the application
-	How to fix:
    -	csrf-token
    - use method ‘POST’ instead of ‘GET’ 

**Password validation when creating account**  
https://docs.djangoproject.com/en/4.2/topics/auth/passwords/#module-django.contrib.auth.password_validation 
-	No rules for credentials e.g. password can be anything
-	How to fix:
    -	Django offers pluggable configurable password validators
    -	defaults:
        -	UserAttributeSimilarityValidator
            o	checks the similarity between the password and a set of attributes of the user (default ‘username’, ‘first_name’, ‘last_name’, ‘email’)
            o	max similarity 0.7, scale from 0.1 to 1.0
        -	MinimumLenghtValidator
            o	default 8
        -	CommonPasswordValidator
            o	compares password to list of 20,000 common passwords
            o	default list https://gist.github.com/roycewilliams/226886fd01572964e1431ac8afc999ce 
        -	NumericPasswordValidator
            o	checks whether the password isn’t entirely numeric
  -	Support for custom validators
  
**Idle user is log out**  
https://docs.djangoproject.com/en/4.2/topics/http/sessions/ 
-	After using the application, instead of logging oneself out, user simply closes the browser. If application session timeouts aren’t set correctly, user remains authenticated.
-	How to fix:
      -	automated log out after predefined idle time using session cookies (3 minutes at the moment for test reasons)
          -	checks the timestamp of the last sent http-request with session cookie, if exceeds the cookie age, shows error page and user must log in again
  
**SQL-injection**
-	Using raw SQL and unsanitized data exposes vulnerability for SQL-injection. If attacker has intuition of database schema, they can get access to the database and e.g. retrieve data or drop data tables.
-	In this application, message sending is vulnerable for SQL-injection
-	How to fix:
    o	utilizing Django ORM  
    o	sanitize data and parametrize SQL-queries
  
**Broken Authentication/Force Browsing**
-	Force browsing to authenticated pages as an unauthenticated user or to privileged pages as a standard user
-	Bypassing access control checks by modifying the URL
-	How to fix:

**Cross-site Scripting Attack (not backend)**
