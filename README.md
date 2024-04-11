# Network Chat Application

This repository contains the source code for a real-time network chat application implemented in Python. The application utilizes AWS EC2 for server deployment and leverages Python's socket programming for client-server communication.

## Prerequisites

Before setting up and using the network chat application, ensure you have the following:

- An AWS account
- Basic knowledge of AWS services
- Python installed on your local machine

## Setup Instructions

Follow these steps to set up and use the network chat application:

### Step 1: Launch an EC2 Instance

1. Log in to your AWS Management Console.
2. Navigate to the EC2 dashboard.
3. Click on "Launch Instance" and choose an Amazon Machine Image (AMI) that supports Python.
4. Configure the instance details, including instance type, VPC, and subnet.
5. Add storage as needed and configure any additional settings.
6. Review and launch the instance.

### Step 2: Configure a VPC

1. Navigate to the VPC dashboard.
2. Click on "Create VPC" and specify the CIDR block.
3. Add subnets, route tables, and gateways as needed.
4. Attach an Internet Gateway to the VPC to enable internet access.

### Step 3: Set Up Security Groups

1. In the EC2 dashboard, navigate to "Security Groups."
2. Create a new security group and configure inbound and outbound rules.
3. Allow TCP ports for communication (e.g., port 8080 for the chat application).

### Step 4: Connect to the Instance

1. Once the instance is running, connect to it using SSH.
2. Upload the chat application files to the instance.

### Step 5: Run the Application

1. Execute the Python script for the server-side of the chat application.
2. Download the client-side Python script from the repository.
3. Open a terminal window and navigate to the directory containing the downloaded script.
4. Run the following command to execute the client script:
   python3 client.py <host> <port>

Replace `<host>` with the IP address or hostname of the server instance, and `<port>` with the port number specified for the chat application.

### Step 6: Test the Application

1. Open multiple client applications and test real-time messaging functionality.

## Additional Resources

- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/)
- [AWS Security Groups Documentation](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html)
