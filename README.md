# TensorFlow Cloud Foundry App


This is a sample app showing how to serve a TensorFlow model in a Python Cloud Foundry
app. This uses the Cloud Foundry offering provided by
[IBM Cloud](https://console.ng.bluemix.net/registration/). The model file and labels
file should be put in the `assets` directory. Currently the files there correspond
to a simple fruit classifier which was created by retraining  *MobileNet_v1_1.0_224*.


## 1. Clone the sample app

Now you're ready to start working with the app. Clone the repo and change to the directory where the sample app is located.
  ```
git clone https://github.com/pvaneck/tensorflow-cf-app
cd tensorflow-cf-app
  ```


## 2. Run the app locally

Install the dependencies listed in the [requirements.txt](https://pip.readthedocs.io/en/stable/user_guide/#requirements-files) file to be able to run the app locally.

You can optionally use a
[virtual environment](https://packaging.python.org/installing/#creating-and-using-virtual-environments)
to avoid having these dependencies clash with those of other Python projects or your operating system.
  ```
pip install -r requirements.txt
  ```

Run the app.
  ```
python app.py
  ```

 View your app at: http://localhost:8000

## 3. Prepare the app for deployment

To deploy to IBM Cloud, it can be helpful to set up a manifest.yml file. One is provided here.
Take a moment to look at it.

The manifest.yml includes basic information about your app, such as the name, how
much memory to allocate for each instance and the route. In this manifest.yml **random-route: true**
generates a random route for your app to prevent your route from colliding with others.
You can replace **random-route: true** with **host: myChosenHostName**, supplying a
host name of your choice. [Learn more...](https://console.bluemix.net/docs/manageapps/depapps.html#appmanifest)

Also, the amount of memory your app uses is dependent on the size of your model. Feel free
to increase or decrease it as you see fit.
 ```
 applications:
 - name: TF-Demo
   random-route: true
   memory: 1024M
 ```

## 4. Deploy the app

You can use the Cloud Foundry CLI to deploy apps.

Choose your API endpoint
   ```
cf api <API-endpoint>
   ```

Replace the *API-endpoint* in the command with an API endpoint from the following list.

|URL                             |Region          |
|:-------------------------------|:---------------|
| https://api.ng.bluemix.net     | US South       |
| https://api.eu-de.bluemix.net  | Germany        |
| https://api.eu-gb.bluemix.net  | United Kingdom |
| https://api.au-syd.bluemix.net | Sydney         |

Login to your IBM Cloud account

  ```
cf login
  ```

From within the *tensorflow-cf-app* directory push your app to IBM Cloud.
  ```
cf push
  ```

This can take a minute. If there is an error in the deployment process you can use the command `cf logs <Your-App-Name> --recent` to troubleshoot.

When deployment completes you should see a message indicating that your app is running.  View your app at the URL listed in the output of the push command.  You can also issue the
  ```
cf apps
  ```
  command to view your apps status and see the URL.
