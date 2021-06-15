import sys, json, os
import subprocess

env = sys.argv[1]

#set input file path
script_dir = os.path.dirname(__file__)
file_path_deploy = os.path.join(script_dir,'..','..','cicd','deploy.json')
file_path_deploy_cmd = os.path.join(script_dir,'..','..','cicd','deploy_cmd.json')

#list step functions
delete_data = ''
create_data = ''
update_data = ''
def read_stepfn_file():
	global delete_data, create_data, update_data
	with open(file_path_deploy, 'r') as f1:
		json_load = json.load(f1)
		delete_data = json_load['stepfunction'][0]['delete']
		create_data = json_load['stepfunction'][1]['create']
		update_data = json_load['stepfunction'][2]['update']

#function for capturing create and update timestamp from a file
creation_time = []
update_time = []
def capture_date():
    f = open(file_path_deploy_cmd, "r")
    check_end = False
    item = ""
    for line in f:
        line = line.strip()
        if line == "{":
            check_end = True
        if line == "}":
            check_end = False
            item += line
            json_load = json.loads(item)
            if 'creationDate' in json_load:
                creation_time.append(json_load['creationDate'])
            if 'updateDate' in json_load:
                update_time.append(json_load['updateDate'])
            item = ""
        if check_end:
            item += line     


#function for validating step function creation
def getStepFunctionCreate():
	step_list = []	
	for i in create_data:
		step_list.append(i['name'])

	if len(step_list) != 0:
		print("\n----------------------StepFunction Creation-----------------------\n")
		if len(step_list) == len(creation_time):
			print("Step Functions created successfully")
		else:
			output = subprocess.check_output(['aws', 'stepfunctions' , 'list-state-machines', '--profile', env])
			response = json.loads(output)
			step_name = []	
			for i in response['stateMachines']:
				step_name.append(i['name'])
						
			for	i in step_list:
				if not i in step_name:
					print(i + " is not created")
		
#function for validating step function update
def getStepFunctionUpdate():
	step_list = []
	for i in update_data:
		step_list.append(i['name'])
	
	print("\n------------------------StepFunction Update-------------------------\n")
	if len(step_list) != 0:	
		if len(step_list) == len(update_time):
			print("Step Functions updated successfully")
		else:
			step_num = len(step_list) - len(update_time)
			print(str(step_num) + " step functions not updated successfully")


#function for validating step function deletion
def getStepFunctionDelete():
	step_list = []
	for i in delete_data:
		step_list.append(i['name'])

	if len(step_list) != 0:
		output = subprocess.check_output(['aws', 'stepfunctions' , 'list-state-machines', '--profile', env])
		response = json.loads(output)	
		step_name = []	
		for i in response['stateMachines']:
			step_name.append(i['name'])
		print("\n-----------------------StepFunction Deletion-----------------------\n")		
		c = 0
		for	i in step_list:
			if i in step_name:
				c += 1
				print(i + " is not deleted")
		if c == 0:
			 print("Deletion is successful")

read_stepfn_file()
capture_date()
getStepFunctionDelete()
getStepFunctionCreate()
getStepFunctionUpdate()
 
