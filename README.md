# django_task_FreJun

## SetUp
<ol> 
  <li>  Install the requirements.txt </li>
  <li> run the management commands initiate_roles and initiate_status after making migrations to make sure
    there is valid data for roles and status in the database </li>
  
 </ol>
 <br>

NOTE: FreJun_task is the name of the project <br>
NOTE: resource is the name of app that handles custom user model and it's serializers <br>
NOTE: project is the name of app that handles all the APIs mentioned in the task <br>
NOTE: All required models are created as per the ORM guidelines given in the pdf <br>
NOTE: Two extra models, namely Role and State have been created to keep track of the user roles and task status <br>
NOTE: .env file is not pushed to repo <br>
NOTE: migrations/ directory is not pushed to repo <br>
 
## Requirements
<ol>
        <li> Users/ Team leaders / Team memberd can be created with django command line interface or admin panel </li>
                <ul>
                        <li> Created custom management command called create_user </li>
                        <li> in the management command we can pass named arguments --name, --email, --role, --password (all are mandetory) </li>
                        <li> Created Custom UserAdmin class to make sure we can create users from the django admin panel </li> 
                </ul>
        
  <br>
  
  <li> Use Token Authentication for all the APIs provided by DRF </li>
                  <ul> 
                    <li> All the viewsets are protected by djangorestframework_simplejwt </li>
                  </ul>
         
  <br>
  
  <li> Create Team API with necessary fields (name, team leader and team members) </li>
                  <ul>
                    <li> API endpoint: localhost:8000/api/project/team/ </li>
                    <li> http method: POST </li>
                    <li> in this endpoint we will have to send data in the following manner </li>
                    <li>{"name": "dummy_team_1", <br>
    "team_lead": "dummy1@gmail.com", <br>
    "team_members": ["dummy2@gmail.com", "dummy3@gmail.com"]} </li>
                    <li> it will only insert team lead if the email provided is of a resource whoes role is 'team_lead' </li>
                    <li> same is the case for team members </li>
                    <li> Only resource with role 'user' can make use of this API endpoint </li>
                  </ul>
  <br>
  
  <li> Create Task API with necessary fields (name and team) - Once task is created, send an email to the team leader of the associated team with task details (async background task)</li>
                  <ul>
                    <li> API endpoint: localhost:8000/api/project/task/ </li>
                    <li> http method: POST </li>
                    <li> in this endpoint we will have to send data in the following manner </li>
                    <li>{
    "name": "dummy task 1", <br>
    "description": "This is dummy description", <br>
    "team": 28, <br>
    "status": "assigned" <br>
} </li>
                    <li> it only allows the following values for status: assigned, under_review, in_progress, done </li>
                    <li> For team we provide the id of the team we want to assign it with </li>
                    <li> Only resource with role 'user' can make use of this API endpoint </li>
                    <li> Integrated celery and created a task to send an email to team lead in an async manner when task is assigned to his/ her team </li>
                  </ul>
  <br>
  <li> Update Task API 
- team leaders will be able to update all task fields 
- team members will be able to update the status only
  </li>
  <ul>
    <li> API endpoint: localhost:8000/api/project/task/ </li>
                    <li> http method: PUT (only team lead of the assigned team can make use of this endpoint to update all fields of a task </li>
                    <li> in this endpoint we will have to send data in the following manner </li>
    <li>{
    "name": "dummy task 1", <br>
    "description": "This is updated descriptionsss", <br>
    "status": "under_review", <br>
    "team_members": [12] <br>

} </li>
     <li> http method: PATCH (only team member that is assigned to this task can make use of this end point to update the status of the task </li>
                    <li> in this endpoint we will have to send data in the following manner </li>
    <li> { <br>
    "status": "done" <br>

}</li>
    <li> even if more fields are provided in the data, this endpoint will only make use of the status key and discard all the others </li>
  </ul>
  <li>Retrieve Tasks API 
- Retrieve a list of all tasks (all fields of Task model included) 
 </li>
  <ul>
    <li> API endpoint: localhost:8000/api/project/task/ </li>
                    <li> http method: GET </li>
    <li> This makes use of read only nested serializers to get all the fields of all the models that are associated with tasks </li>
    
  
  
  </ul>
  
          
  
  
 </ol>
