blocks = [
        {
			"type": "image",
			"image_url": "image_1",
			"alt_text": "slack_image"
		},
		{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": " repalceable value"
            }
        },
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Click on this link to sign in to aws console and change your password so you don't get locked out.*"
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "AWS Console"
					
				},
				"url": "https://someworkspace.signin.aws.amazon.com/console",
				"style": "primary"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Follow this link if you need a guide to change your password.*"
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Documentation"
					
				},
				"url": "https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_passwords_admin-change-user.html#:~:text=To%20change%20the%20password%20for%20an%20IAM%20user%20(console)",
				
				
			}
		}
	]