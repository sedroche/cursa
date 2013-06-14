<?php

/**
 * create_resource web service plugin
 * Author John Roche
 * Created on 21 May 2013
 */

require_once($CFG->dirroot . '/local/clarity/resource_handler.php');


class local_clarity_external extends external_api {

    /**
     * Returns description of method parameters
     * @return external_function_parameters
     */
    public static function create_resource_parameters() {
        return new external_function_parameters(
                array(  'courseid' => new external_value(PARAM_INT, 'The id of the course'),
                	    'sectionid' => new external_value(PARAM_INT, 'The section id'),
                	    'type' => new external_value(PARAM_TEXT, 'The type of resource. file, folder, label'),
                	    'displayname' => new external_value(PARAM_TEXT, 'The name that is displayed beside the resource', VALUE_OPTIONAL),
                	    'mainfile' => new external_value(PARAM_TEXT, 'The main file that is selected. This will turn a folder into a Lab or Presentation', VALUE_OPTIONAL),
                	    'mainfilepath' => new external_value(PARAM_TEXT, 'The path to the main file from the root of the folder. Must start and end with /', VALUE_OPTIONAL),
                		'labeltext' => new external_value(PARAM_RAW, "The label text. Used with type 'label'", VALUE_OPTIONAL),
                		'labeltextformat' => new external_value(PARAM_TEXT, "The format of the label text - markdown or html. Used with type 'label'", VALUE_OPTIONAL)
                		)
        );
    }

    /**
     * Returns course id, section id, and course module id  of the created resource
     * @return Array of course id, section id, course module id
     */
    public static function create_resource($courseid, $sectionid, $type, $displayname, $mainfile, $mainfilepath, $labeltext, $labeltextformat) {
        global $USER;
		global $CFG;
		global $DB;
        //Parameter validation
        //REQUIRED
        $params = self::validate_parameters(self::create_resource_parameters(),
                array('courseid' => $courseid,
                	  'sectionid' => $sectionid,
                	  'type' => $type,
                	  'displayname' => $displayname,
                	  'mainfile' => $mainfile,
                	  'mainfilepath' => $mainfilepath,
                	  'labeltext' => $labeltext,
                	  'labeltextformat' => $labeltextformat
                	)
        		);

        //Context validation
        //OPTIONAL but in most web service it should be present
        $context = get_context_instance(CONTEXT_USER, $USER->id);
        self::validate_context($context);
        
        if($params['type'] === 'label'){
        	$handler = new resource_handler($params, 'label');
        	$handler->create_course_module();
        	$instanceid = $handler->add_resource(null, $labeltext, $labeltextformat);
        	$course_module_data = $handler->finish_adding_course_module($instanceid);
        }
        else{
        	$handler = new resource_handler($params, 'resource');
        	$handler->upload();
        	$draftitemid = $handler->copy_file_to_draft_area();
        	$handler->create_course_module();
        	$instanceid = $handler->add_resource($draftitemid, null, null);
        	$course_module_data = $handler->finish_adding_course_module($instanceid);
        	$handler->delete_private_user_file();
        }
		
        return $course_module_data ;;
    }

    /**
     * Returns description of method result value
     * @return external_description
     */
    public static function create_resource_returns() {
        return new external_function_parameters(
        		array(
        				'courseid' => new external_value(PARAM_TEXT, 'The id of the course that the resource was added to'),
        				'sectionid' => new external_value(PARAM_TEXT, 'The id of the section that the resource was added to'),
        				'cmid' => new external_value(PARAM_TEXT, 'The id of the coursemodule that the resource was added to')
            		)
        		);
    }



}

