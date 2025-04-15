# A Telegram bot for the-Fizz notification

After deployment, reply '\start' to the bot and it would notify you when there are available room(s)/studio(s)/apartment(s) on the website.

# Obtain a Token for the Telegram Bot

[RTFM](https://core.telegram.org/bots)

# Deploying Telegram Bot on AWS EC2

This guide will walk you through setting up your Telegram bot on an AWS EC2 instance so it can run continuously.

## Step 1: Set Up an AWS Account

If you don't already have an AWS account:

1. Go to [AWS Console](https://aws.amazon.com/)
2. Click "Create an AWS Account" and follow the registration steps
3. You'll need to provide credit card information, but AWS offers a free tier for new accounts

## Step 2: Launch an EC2 Instance

1. Log in to the AWS Management Console
2. Navigate to the EC2 Dashboard
3. Click "Launch Instance"
4. Choose an Amazon Machine Image (AMI):
   - Select "Amazon Linux 2023" (free tier eligible)
5. Choose an Instance Type:
   - Select "t3.micro" (free tier eligible)
6. Configure Instance:
   - Default settings are usually fine
7. Add Storage:
   - Default 8GB is sufficient for your bot
8. Add Tags:
   - Add a tag with key "Name" and value "TelegramBot"
9. Configure Security Group:
   - Create a new security group
   - Allow SSH (port 22) from your IP address only
10. Review and Launch:
    - Review your settings and click "Launch"
11. Create a new key pair, download it, and keep it safe
    - Name it something like "botFizz.pem"
    - This key is required to access your instance

## Step 3: Connect to Your EC2 Instance

### From Windows:

1. Download and install [PuTTY](https://www.putty.org/)
2. Convert your .pem key to .ppk format using PuTTYgen
   - On Windows:
     Use PuTTYgen to convert your botFizz.pem to a .ppk file: - Open PuTTYgen - Click "Load" and select your botFizz.pem file - Click "Save private key" and save as botFizz.ppk
3. Use PuTTY to connect to your instance using the Public DNS/IP
   - Host Name: ec2-user@[your-instance-public-dns]
   - Port: 22
   - Connection > SSH > Auth: Browse to your .ppk file
   - Save the session for easier access later

### From Mac/Linux:

1. Open Terminal
2. Change permissions for the key file:
   ```
   chmod 400 /path/to/telegram-bot-key.pem
   ```
3. Connect to your instance:
   ```
   ssh -i /path/to/telegram-bot-key.pem ec2-user@[your-instance-public-dns]
   ```

## Step 4: Install Required Software

Once connected to your EC2 instance, run these commands:

```bash
# Update the system
sudo yum update -y

# Install Python and pip
sudo yum install python3 python3-pip -y

CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
echo "Chrome version: $CHROME_VERSION"

# Download matching ChromeDriver
wget -N "https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION.0.7049.0/linux64/chromedriver-linux64.zip"
unzip chromedriver-linux64.zip
chmod +x chromedriver-linux64/chromedriver
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
rm -rf chromedriver-linux64
```

## Step 5: Upload Your Bot Code

There are several ways to upload your code:

### Option 1: Using SCP (from your local machine)

```bash
scp -i /path/to/telegram-bot-key.pem -r /path/to/your/bot ec2-user@[your-instance-public-dns]:~/bot
```

### Option 2: Using Git (if your code is in a repository)

```bash
# On EC2 instance
sudo yum install git -y
git clone https://github.com/your-username/your-repo.git
```

### Option 3: Create files directly on EC2

Create a directory for your bot:

```bash
mkdir ~/telegram-bot
cd ~/telegram-bot
```

Then create the necessary files using a text editor like nano or vim:

```bash
nano main.py
# Paste your main.py content, save with Ctrl+O, exit with Ctrl+X

nano scraper.py
# Paste your scraper.py content, save and exit

nano requirements.txt
# Paste your requirements.txt content, save and exit
```

## Step 6: Install Python Dependencies

```bash
cd ~/telegram-bot  # or wherever your code is
pip3 install requirements.txt
```

## Step 7: Run Your Bot as a Background Service

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

Add the following content (adjust paths as needed):

```
[Unit]
Description=Telegram Fizz Bot Service
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/telegram-bot
ExecStart=/usr/bin/python3 /home/ec2-user/telegram-bot/main.py
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=telegrambot
Environment=PYTHONUNBUFFERED=1
Environment=TG_TOKEN=YOUR_TOKEN
Environment=CHECK_INTERVAL=120
Environment=CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

Check the status:

```bash
sudo systemctl status telegram-bot
```

View logs:

```bash
sudo journalctl -u telegram-bot -f
```

## Step 8: Keep Your EC2 Instance Running

By default, your EC2 instance will continue running until you stop or terminate it. There are no idle timeouts.

## Step 9: Set Up Monitoring (Optional)

You can set up CloudWatch to monitor your EC2 instance:

1. In the EC2 Dashboard, select your instance
2. Go to the "Monitoring" tab
3. Click "Manage detailed monitoring"
4. Enable detailed monitoring (there may be additional costs)

## Maintenance Tips

1. **Updating your bot code**:

   - Upload the new files
   - Restart the service: `sudo systemctl restart telegram-bot`

2. **Checking logs**:

   - View real-time logs: `sudo journalctl -u telegram-bot -f`
   - View error logs: `sudo journalctl -u telegram-bot -p err`

3. **System updates**:

   - Regularly update your system: `sudo yum update -y`

4. **Backup your instance**:

   - Create an AMI (Amazon Machine Image) from your EC2 instance periodically

5. **Cost management**:
   - Monitor your AWS usage in the billing dashboard
   - Set up billing alerts to avoid unexpected charges

# DELETE THIS VIRTUAL MACHINE IN NO MORE THAN ONE YEAR TO AVOID EXTRA BILLS (AWS OFFERS 12-MONTH LONG FREE TRIAL)
