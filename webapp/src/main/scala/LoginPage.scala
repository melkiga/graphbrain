package com.graphbrain.webapp

case class LoginPage() extends Page {
	override def html = {

<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
<title>GraphBrain</title>
<link href="/css/login.css?101111" type="text/css" rel="Stylesheet" />  
<link rel="shortcut icon" href="/favicon.ico" type="image/x-icon" />
</head>
<body>

<div id="logo">
	<img src="/images/GB_logo_L.png" alt="graphbrain"/>
</div>

<div id="slogan">
A beautiful new way to organize and explore information.
</div>

<div id="left">
<div id="email">
	GraphBrain is under development. If you would like to keep in touch, just please give us your email. We will send you an invite as soon as possible and let you know of any major project milestones. We won't give your email to any third parties and we will keep the message volume very low.
	<br /><br />
	<form action="/addemail" method="post" id="login_form">
		Your email: <input type="text" name="email" size="25" />
		<input type="submit" value="send" />
	</form>
	<div class="error">{{ email_error }}</div>
	<div class="message">{{ email_message }}</div>
</div>
</div>

<div id="right">
<div id="login">
	If you already have a GraphBrain account, please login here.
	<br /><br />
	<form action="/login" method="post" id="login_form">
		<label for="email">Username</label> <input type="text" name="email" size="25" /><br />
		<label for="password">Password</label> <input type="password" name="password" size="25" /><br />
		<input type="submit" value="Login" />
	</form>
	<div class="error">{{ login_error }}</div>
</div>
</div>

<br />

</body>
</html>

  }
}