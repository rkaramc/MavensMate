import urlparse
import sys
import util
import json
#import cgi
#import time
import multiprocessing
#from multiprocessing import Queue
#from multiprocessing import Manager
sys.path.append('../')
from util import BackgroundWorker
#from urlparse import urlparse, parse_qs
import lib.config as gc

# async_request_queue holds list of active async requests
async_request_queue = {}

####################
## ASYNC REQUESTS ##
####################

def project_request(request_handler):
    '''
        POST /project
        {
            "project_name"  : "my project name"
            "username"      : "mm@force.com",
            "password"      : "force",
            "org_type"      : "developer",
            "package"       : {
                "ApexClass"     : "*",
                "ApexTrigger"   : ["Trigger1", "Trigger2"]
            }
        }
    '''
    run_async_operation(request_handler, 'new_project')

def project_existing_request(request_handler):
    '''
        POST /project/existing
        {
            "project_name"  : "my project name"
            "username"      : "mm@force.com",
            "password"      : "force",
            "org_type"      : "developer",
            "directory"     : "/path/to/project",
            "action"        : "existing"
        }
    '''
    run_async_operation(request_handler, 'new_project_from_existing_directory')

def project_edit_request(request_handler):
    '''
        POST /project/edit
        (body same as project_request)
    '''
    run_async_operation(request_handler, 'edit_project')

def project_upgrade_request(request_handler):
    '''
        POST /project/upgrade
        {
            "project_name"  : "my project name"
            "username"      : "mm@force.com",
            "password"      : "force",
            "org_type"      : "developer"
        }
    '''
    run_async_operation(request_handler, 'upgrade_project')

def execute_apex_request(request_handler):
    '''
        POST /apex/execute
        {
            "project_name"    : "my project name"
            "log_level"       : "DEBUG",
            "log_category"    : "APEX_CODE",
            "body"            : "String foo = 'bar';",
        }
    '''
    run_async_operation(request_handler, 'execute_apex')


def deploy_request(request_handler):
    '''
        POST /project/deploy
        call to deploy metadata to a server
        {
            "check_only"            : true,
            "rollback_on_error"     : true,
            "destinations"          : [
                {
                    "username"              : "username1@force.com",
                    "org_type"              : "developer"
                }
            ],
            "package"               : {
                "ApexClass" : "*"
            }
        }
    '''
    run_async_operation(request_handler, 'deploy')

def unit_test_request(request_handler):
    '''
        POST /project/unit_test
        {
            "classes" : [
                "UnitTestClass1", "UnitTestClass2"
            ],
            "run_all_tests" : false
        }
    '''
    gc.logger.debug('in unit test method!')
    run_async_operation(request_handler, 'unit_test')
    
def metadata_index_request(request_handler):
    '''
        call to update the project .metadata index
    '''
    run_async_operation(request_handler, 'index_metadata')

def new_log_request(request_handler):
    '''
        call to create a new debug log
    '''
    run_async_operation(request_handler, 'new_log')


##########################
## SYNCHRONOUS REQUESTS ##
##########################

def get_active_session_request(request_handler):
    '''
        GET /session?username=mm@force.com&password=force&org_type=developer
    '''
    request_id = util.generate_request_id()
    params, json_body, plugin_client = get_request_params(request_handler)
    worker_thread = BackgroundWorker('get_active_session', params, False, request_id, json_body, plugin_client)
    worker_thread.start()
    worker_thread.join()
    response = worker_thread.response
    respond(request_handler, response)

def update_credentials_request(request_handler):
    '''
        POST /project/creds
        {
            "project_name"  : "my project name"
            "username"      : "mm@force.com",
            "password"      : "force",
            "org_type"      : "developer",
        }
        NOTE: project name should not be updated, as it is used to find the project in question
        TODO: maybe we assign a unique ID to each project which will give users the flexibility
              to change the project name??
        TODO: we may need to implement a "clean" flag which will clean the project after creds
              have been updated
    '''
    request_id = util.generate_request_id()
    params, raw_post_body, plugin_client = get_request_params(request_handler)
    worker_thread = BackgroundWorker('update_credentials', params, False, request_id, raw_post_body, plugin_client)
    worker_thread.start()
    worker_thread.join()
    response = worker_thread.response
    respond(request_handler, response)

def project_edit_subscription(request_handler):
    '''
        POST /project/subscription
        {
            "project_name"  : "my project name"
            "subscription"  : ["ApexClass", "ApexPage"]
        }
    '''
    request_id = util.generate_request_id()
    params, raw_post_body, plugin_client = get_request_params(request_handler)
    worker_thread = BackgroundWorker('update_subscription', params, False, request_id, raw_post_body, plugin_client)
    worker_thread.start()
    worker_thread.join()
    response = worker_thread.response
    respond(request_handler, response)


def connections_list_request(request_handler):
    request_id = util.generate_request_id()
    params, raw_post_body, plugin_client = get_request_params(request_handler)
    worker_thread = BackgroundWorker('list_connections', params, False, request_id, raw_post_body, plugin_client)
    worker_thread.start()
    worker_thread.join()
    response = worker_thread.response
    respond(request_handler, response)

def connections_new_request(request_handler):
    request_id = util.generate_request_id()
    params, raw_post_body, plugin_client = get_request_params(request_handler)
    worker_thread = BackgroundWorker('new_connection', params, False, request_id, raw_post_body, plugin_client)
    worker_thread.start()
    worker_thread.join()
    response = worker_thread.response
    respond(request_handler, response)

def connections_delete_request(request_handler):
    request_id = util.generate_request_id()
    params, raw_post_body, plugin_client = get_request_params(request_handler)
    worker_thread = BackgroundWorker('delete_connection', params, False, request_id, raw_post_body, plugin_client)
    worker_thread.start()
    worker_thread.join()
    response = worker_thread.response
    respond(request_handler, response)

def metadata_list_request(request_handler):
    '''
        GET /metadata/list
        {
            "sid"             : "",
            "metadata_type"   : "",
            "murl"            : ""
        }
        call to get a list of metadata of a certain type
    '''
    request_id = util.generate_request_id()
    params, json_body, plugin_client = get_request_params(request_handler)
    worker_thread = BackgroundWorker('list_metadata', params, False, request_id, json_body, plugin_client)
    worker_thread.start()
    worker_thread.join()
    response = worker_thread.response
    respond(request_handler, response)

def get_metadata_index(request_handler):
    '''
        GET /project/get_index
        {
            "project_name"  : "my project name",
            "keyword"       : "mykeyword" //optional
        }
        call to get the metadata index for a project
    '''
    request_id = util.generate_request_id()
    params, json_body, plugin_client = get_request_params(request_handler)
    worker_thread = BackgroundWorker('get_indexed_metadata', params, False, request_id, json_body, plugin_client)
    worker_thread.start()
    worker_thread.join()
    response = worker_thread.response
    respond(request_handler, response) 

def refresh_metadata_index(request_handler):
    '''
        GET /project/get_index/refresh
        {
            "project_name"      : "my project name",
            "metadata_types"    : ["ApexClass"]
        }
        call to refresh a certain type of metadata
    '''
    request_id = util.generate_request_id()
    params, json_body, plugin_client = get_request_params(request_handler)
    worker_thread = BackgroundWorker('refresh_metadata_index', params, False, request_id, json_body, plugin_client)
    worker_thread.start()
    worker_thread.join()
    response = worker_thread.response
    respond(request_handler, response) 


##########################
## END REQUEST HANDLERS ##
##########################


def run_async_operation(request_handler, operation_name):
    gc.logger.debug('>>> running an async operation')
    request_id = util.generate_request_id()
    params, raw_post_body, plugin_client = get_request_params(request_handler)
    gc.logger.debug(request_id)
    gc.logger.debug(params)
    gc.logger.debug(raw_post_body)
    
    worker_thread = BackgroundWorker(operation_name, params, True, request_id, raw_post_body, plugin_client)
    gc.logger.debug('worker created')
    worker_thread.start()
    gc.logger.debug('worker thread started')
    async_request_queue[request_id] = worker_thread
    gc.logger.debug('placed into queue')

    #q = Queue() #on larger object puts, process would hang
    #using manager based on this recommendation:
    #http://stackoverflow.com/questions/11442892/python-multiprocessing-queue-failure
    # manager = Manager()
    # q = manager.Queue() #TODO: request is failing here many times
    # gc.logger.debug('finished with queue')
    #worker = BackgroundWorker(operation_name, params, True, request_id, raw_post_body, q)
    #gc.logger.debug('worker created')
    #p = multiprocessing.Process(target=process_request_in_background,args=(worker,))
    #p.start()
    #gc.logger.debug('started process!')
    #add_to_request_queue(request_id, p, q)
    #gc.logger.debug('preparing to response with the async id!')
    return respond_with_async_request_id(request_handler, request_id)

#client polls this servlet to determine whether the request is done
#if the request IS done, it will respond with the body of the request
def status_request(request_handler):
    gc.logger.debug('>>> status request')
    params, json_string, plugin_client = get_request_params(request_handler)
    gc.logger.debug('>>> params: ')
    gc.logger.debug(params)
    try:
        request_id = params['id']
    except:
        request_id = params['id'][0]
    gc.logger.debug('>>> request id: ' + request_id)
    gc.logger.debug('>>> async queue: ')
    gc.logger.debug(async_request_queue)

    if request_id not in async_request_queue:
        response = { 'status' : 'error', 'id' : request_id, 'body' : 'Request ID was not found' }
        response_body = json.dumps(response)
        respond(request_handler, response_body, 'text/json')
    else:
        async_thread = async_request_queue[request_id]
        gc.logger.debug('found async thread, is it alive????')
        gc.logger.debug(async_thread.is_alive())
        if async_thread.is_alive():
            gc.logger.debug('>>> request is not ready')
            print '>>>> NOT READY....'
            respond_with_async_request_id(request_handler, request_id)
        elif async_thread.is_alive() == False:
            gc.logger.debug('>>> request is probably ready, returning response!!')
            print '>>>> DONE!!!'
            async_request_queue.pop(request_id, None)
            # result = []
            # for i in iter(queue.get, 'STOP'):
            #     result.append(i)
            #     time.sleep(.1)
            respond(request_handler, async_thread.response, 'text/json')

def add_to_request_queue(request_id, p, q):
    async_request_queue[request_id] = { 'process' : p, 'queue' : q }

def get_request_params(request_handler):
    print '>>>>>> ', request_handler.path
    print '>>>>>> ', request_handler.command
    #print '>>>>>> ', request_handler.headers
    plugin_client = request_handler.headers.get('mm_plugin_client', 'SUBLIME_TEXT_2')
    if request_handler.command == 'POST':
        data_string = request_handler.rfile.read(int(request_handler.headers['Content-Length']))
        #print '>>>>>>> ', data_string
        postvars = json.loads(data_string)
        if 'package' in postvars:
            postvars['package'] = json.dumps(postvars['package'])
        return postvars, data_string, plugin_client
    elif request_handler.command == 'GET':
        params = parse_qs(urlparse(request_handler.path).query)
        for key in params:
            if '[]' in key:
                params[key] = params[key]
            else:
                params[key] = params[key][0]
        return_params = {}
        for key in params:
            if '[]' in key:
                return_params[key.replace('[]','')] = params[key]
            else:
                return_params[key] = params[key]       
        json_string = json.dumps(return_params)
        return params, json_string, plugin_client

def process_request_in_background(worker):
    worker.run()




######################
## RESPONSE METHODS ##
######################

#this returns the request id after an initial async request
def respond_with_async_request_id(request_handler, request_id):
    gc.logger.debug('responding with async request id!')
    response = { 'status' : 'pending', 'id' : request_id }
    json_response_body = json.dumps(response)
    gc.logger.debug(json_response_body)
    respond(request_handler, json_response_body, 'text/json')

def respond(request_handler, body, type='text/json'):
    gc.logger.debug('responding!')
    #gc.logger.debug(body)
    #print '>>>>>>>> responding with, ' body
    request_handler.send_response(200)
    request_handler.send_header('Content-type', type)
    request_handler.send_header('Access-Control-Allow-Origin', '*')
    request_handler.end_headers()
    request_handler.wfile.write(body)
    return



##################
## PATH MAPPING ##
##################

mappings = {
    '/status'                   : { 'GET'   : status_request },     
    '/project'                  : { 'POST'  : project_request }, 
    '/project/edit'             : { 'POST'  : project_edit_request }, 
    '/project/subscription'     : { 'POST'  : project_edit_subscription }, 
    '/project/creds'            : { 'POST'  : update_credentials_request },
    '/project/deploy'           : { 'POST'  : deploy_request },
    '/project/unit_test'        : { 'POST'  : unit_test_request },
    '/project/get_index'        : { 'POST'  : get_metadata_index },
    '/project/refresh_index'    : { 'POST'  : refresh_metadata_index },    
    '/project/index'            : { 'POST'  : metadata_index_request },
    '/project/conns/list'       : { 'GET'   : connections_list_request },
    '/project/conns/new'        : { 'POST'  : connections_new_request },
    '/project/conns/delete'     : { 'POST'  : connections_delete_request },
    '/project/upgrade'          : { 'POST'  : project_upgrade_request },
    '/project/existing'         : { 'POST'  : project_existing_request },
    '/project/new_log'          : { 'POST'  : new_log_request },
    '/session'                  : { 'GET'   : get_active_session_request },
    '/apex/execute'             : { 'POST'  : execute_apex_request },
    '/metadata/list'            : { 'GET'   : metadata_list_request }
}

if __name__ == "__main__":
    # add freeze support
    multiprocessing.freeze_support()