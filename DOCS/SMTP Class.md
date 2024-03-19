
# SMTP Class
(This is placeholder info for now)

-----
Please check out the `usage.py` file in the `smtp` directory for a basic example of how to use the SMTP class.

#### Methods
##### `send_template(to, subject, template, data={})`
This method sends an email using one of the template files. It takes the following parameters:
- `to`: The recipient's email address.
- `subject`: The subject of the email.
- `template`: The name of the template file (without the file extension).
- `data` (optional): A dictionary containing data to replace the placeholder tags in the template.
##### `send_email(to, subject, body)`
This method sends an email using a custom body. It takes the following parameters:
- `to`: The recipient's email address.
- `subject`: The subject of the email.
- `body`: The body of the email.
##### `shutdown()`
This method closes the connection to the SMTP server.

#### What are templates?
Templates consist of HTML pages that have replacable placeholder tags inside. Any time you tell the class to send a template, it will replace the placeholder tags with matching values from the `data` dictionary you provide. For example, if you have a template with the following HTML, titled `example.html`:
```html
<!DOCTYPE html>
<html>
    <head>
        <title>Test Email</title>
    </head>
    <body>
        <h1>Hello, {{name}}!</h1>
        <p>Here is a link to our website: <a href="{{link}}">Click here</a></p>
    </body>
</html>
```
You can send this template with the following method:
```python
smtp_driver.send_template(to='john@example.com', subject='', template='example.html', data={'name': 'John', 'link': 'http://example.com'})
```
The `{{name}}` and `{{link}}` tags will be replaced with the values you provide in the `data` dictionary. The resulting HTML will be sent to the email address you specify.

#### Additional Note(s)
- If you want to use Gmail to send message, note that they require App Passwords. You can generate one by going to your Google Account settings and navigating to 2-Step Verification. From there, you can generate an App Password for your application. You will need to use this password in the `.env` file for the `SMTP_PASSWORD` variable.
- If you want to use Gmail to send a message, set the following environment vars:
  - SMTP_PASSWORD=``{{the App Password from gmail}}``
  - SMTP_USERNAME=``{{your email}}``
  - SMTP_SERVER="smtp.gmail.com"
  - SMTP_PORT=465