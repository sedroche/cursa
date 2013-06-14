<?php

/**
 * resource_handler class
 * This class is responsible for creating a resource
 * The resource_handler class can create a file or label resource
 * Author John Roche
 * Created on 21 May 2013
 */

require_once($CFG->libdir . "/externallib.php");
require_once($CFG->dirroot.'/repository/lib.php');
require_once($CFG->dirroot.'/mod/label/lib.php');
require_once($CFG->dirroot.'/repository/upload/lib.php');
require_once($CFG->dirroot.'/course/lib.php');
require_once($CFG->dirroot.'/lib/filelib.php');
require_once($CFG->dirroot.'/lib/filebrowser/file_browser.php');
require_once($CFG->dirroot.'/lib/filestorage/file_storage.php');
require_once($CFG->dirroot.'/lib/filestorage/zip_packer.php');
require_once($CFG->dirroot . '/config.php');
require_once($CFG->dirroot . '/webservice/lib.php');

class resource_handler {
	/** @var object The course that we are uploading to */
	protected $course = null;
	
	/** @var context_course The course context for capability checking */
	protected $context = null;
	
	/** @var int The file context id */
	public $filecontextid = null;
	
	/** @var string The file component */
	public $filecomponent = null;
	
	/** @var string The file area */
	public $filearea = null;
	
	/** @var string The file path */
	public $filepath = null;
	
	/** @var string The file name */
	public $filename = null;
	
	/** @var int The file itemid */
	public $fileitemid = null;
	
	/** @var int The section number we are uploading to */
	protected $section = null;
	
	/** @var string The type of upload (e.g. 'Files', 'text/plain') */
	protected $type = null;
	
	/** @var object The details of the module type that will be created */
	protected $module= null;
	
	/** @var string The file to be assigned as main in a folder */
	protected $mainfile = null;
	
	/** @var string The file to be assigned as main in a folder */
	protected $mainfilepath = null;
	
	/** @var object The course module that has been created */
	protected $cm = null;
	
	/** @var string The name to be displayed beside the resource */
	protected $displayname = null;


	
	
	public function __construct($moduledata, $modulename) {
		global $DB;
		
		$this->course = $DB->get_record('course', array('id' => $moduledata['courseid']), '*', MUST_EXIST);
        $this->context = context_course::instance($this->course->id);
        $this->section = $moduledata['sectionid'];
        $this->type = $moduledata['type'];
        $this->displayname = $moduledata['displayname'];
        $this->mainfile = $moduledata['mainfile'];
        $this->mainfilepath = $moduledata['mainfilepath'];

        if (!$this->module = $DB->get_record('modules', array('name' => $modulename))) {
            throw new coding_exception("Module $this->module does not exist");
        }
        
		if (!course_allowed_module($this->course, $this->module->name)) {
	            throw new coding_exception("The module {$this->module->name} is not allowed to be added to this course");
		}
	}
	
	
	public function copy_file_to_draft_area(){
		global $USER;
		
		// This is the code from lib/filelib/filelib.php
		// file_prepare_draft_area(&$draftitemid, $contextid, $component, $filearea, $itemid, array $options=null, $text=null);
		// It looks like that function does nothing if a draftitemid is passed as a parameter
		// I needed the draftitemid returned, so I used the code here instead
		$fs = get_file_storage();
		$usercontext = context_user::instance($USER->id);
		$draftitemid = file_get_unused_draft_itemid();
		$file_record = array('contextid'=>$usercontext->id, 'component'=>'user', 'filearea'=>'draft', 'itemid'=>$draftitemid);
		
		if ($files = $fs->get_area_files($this->filecontextid , $this->filecomponent, $this->filearea, $this->fileitemid)) {
			foreach ($files as $file) {
				$draftfile = $fs->create_file_from_storedfile($file_record, $file);
				if ($this->type === 'folder'){
					$packer = get_file_packer();
					$packer->extract_to_storage($draftfile, $draftfile->get_contextid(), $draftfile->get_component(), $draftfile->get_filearea(), $draftfile->get_itemid(), $draftfile->get_filepath());
					//$filepath = file_correct_filepath($draftfile->get_filepath());
					if ($this->mainfile){
						// reset sort order
						file_reset_sortorder($usercontext->id, 'user', 'draft', $draftfile->get_itemid());
						// set main file
						$return = file_set_sortorder($usercontext->id, 'user', 'draft', $draftfile->get_itemid(), $this->mainfilepath, $this->mainfile, 1);
						$draftfile->delete();
					}

				}
				
				// XXX: This is a hack for file manager (MDL-28666)
				// File manager needs to know the original file information before copying
				// to draft area, so we append these information in mdl_files.source field
				// {@link file_storage::search_references()}
				// {@link file_storage::search_references_count()}
				$sourcefield = $file->get_source();
				$newsourcefield = new stdClass;
				$newsourcefield->source = $sourcefield;
				$original = new stdClass;
				$original->contextid = $contextid;
				$original->component = $component;
				$original->filearea  = $filearea;
				$original->itemid    = $itemid;
				$original->filename  = $file->get_filename();
				$original->filepath  = $file->get_filepath();
				$newsourcefield->original = file_storage::pack_reference($original);
				$draftfile->set_source(serialize($newsourcefield));
			}
		}
		
		return $draftitemid ;
	}
	
	public function create_course_module(){
		$this->cm = new stdClass();
		$this->cm->course = $this->course->id;
		$this->cm->section = $this->section;
		$this->cm->module = $this->module->id;
		$this->cm->modulename = $this->module->name;
		$this->cm->instance = 0; // This will be filled in after we create the instance.
		$this->cm->visible = 1;
		$this->cm->groupmode = $this->course->groupmode;
		$this->cm->groupingid = $this->course->defaultgroupingid;
		
		// Set the correct default for completion tracking.
		$this->cm->completion = COMPLETION_TRACKING_NONE;
		$completion = new completion_info($this->course);
		if ($completion->is_enabled()) {
			if (plugin_supports('mod', $this->cm->modulename, FEATURE_MODEDIT_DEFAULT_COMPLETION, true)) {
				$this->cm->completion = COMPLETION_TRACKING_MANUAL;
			}
		}
		
		if (!$this->cm->id = add_course_module($this->cm)) {
			throw new coding_exception("Unable to create the course module");
		}
		// The following are used inside some few core functions, so may as well set them here.
		$this->cm->coursemodule = $this->cm->id;
		$groupbuttons = ($this->course->groupmode or (!$this->course->groupmodeforce));
		if ($groupbuttons and plugin_supports('mod', $this->module->name, FEATURE_GROUPS, 0)) {
			$this->cm->groupmodelink = (!$this->course->groupmodeforce);
		} else {
			$this->cm->groupmodelink = false;
			$this->cm->groupmode = false;
		}
	}
	
	
	public function get_file_from_private_area($filedatafromparams){
		$fs = get_file_storage();
		
		// Prepare file record object
		$fileinfo = array(
				'component' => 'user',
				'filearea' => 'private',     // usually = table name
				'itemid' => 0,               // usually = ID of row in table
				'contextid' => 5, // ID of context
				'filepath' => '/',           // any path beginning and ending in /
				'filename' => 'lab.zip'); // any filename
			
		// Get file
		$file = $fs->get_file($fileinfo['contextid'], $fileinfo['component'], $fileinfo['filearea'],
				$fileinfo['itemid'], $fileinfo['filepath'], $fileinfo['filename']);
		$file->delete();
	}
	
	
	public function add_resource($draftitemid, $labeltext, $labeltextformat){
		$resource = new stdClass();
		$resource->course = $this->course->id;
		$resource->name = $this->displayname;
		$resource->description = '';
		$resource->coursemodule = $this->cm->id;
		if($labeltext){
			if($labeltextformat === 'markdown'){
				$resource->introformat = FORMAT_MARKDOWN;
			}
			else if ($labeltextformat === 'html'){
				$resource->introformat = FORMAT_HTML;
			}

			$resource->intro = $labeltext;
		}
		else{
			$resource->files = $draftitemid;
		}
		
		// Set the display options to the site defaults.
		$config = get_config('resource');

		if ($this->type === 'folder'){
			$resource->display = 5;
		}
		else{
			$resource->display = $config->display;
		}
		$resource->popupheight = $config->popupheight;
		$resource->popupwidth = $config->popupwidth;
		$resource->printheading = $config->printheading;
		$resource->printintro = $config->printintro;
		$resource->showsize = (isset($config->showsize)) ? $config->showsize : 0;
		$resource->showtype = (isset($config->showtype)) ? $config->showtype : 0;
		$resource->filterfiles = $config->filterfiles;
		$addinstancefunction    = $this->module->name."_add_instance";
		$instanceid = $addinstancefunction($resource, null);
		return $instanceid;
	}
	
	
	public function finish_adding_course_module($instanceid){
		global $USER;
		global $DB;
		
		if (!$instanceid) {
			// Something has gone wrong - undo everything we can.
			course_delete_module($this->cm->id);
			throw new moodle_exception('errorcreatingactivity', 'moodle', '', $this->module->name);
		}
		
		// Note the section visibility
		$visible = get_fast_modinfo($this->course)->get_section_info($this->cm->section)->visible;
		
		$DB->set_field('course_modules', 'instance', $instanceid, array('id' => $this->cm->id));
		// Rebuild the course cache after update action
		rebuild_course_cache($this->course->id, true);
		$course->modinfo = null; // Otherwise we will just get the old version back again.
		
		$sectionid = course_add_cm_to_section($this->course, $this->cm->id, $this->section);
		
		set_coursemodule_visible($this->cm->id, $visible);
		if (!$visible) {
			$DB->set_field('course_modules', 'visibleold', 1, array('id' => $this->cm->id));
		}
		
		// retrieve the final info about this module.
		$info = get_fast_modinfo($this->course);
		if (!isset($info->cms[$this->cm->id])) {
			// The course module has not been properly created in the course - undo everything.
			course_delete_module($this->cm->id);
			throw new moodle_exception('errorcreatingactivity', 'moodle', '', $this->module->name);
		}
		$mod = $info->get_cm($this->cm->id);
		$mod->groupmodelink = $this->cm->groupmodelink;
		$mod->groupmode = $this->cm->groupmode;
		
		// Trigger mod_created event with information about this module.
		$eventdata = new stdClass();
		$eventdata->modulename = $mod->modname;
		$eventdata->name       = $mod->name;
		$eventdata->cmid       = $mod->id;
		$eventdata->courseid   = $this->course->id;
		$eventdata->userid     = $USER->id;
		events_trigger('mod_created', $eventdata);
		
		add_to_log($this->course->id, "course", "add mod",
		"../mod/{$mod->modname}/view.php?id=$mod->id",
		"{$mod->modname} $instanceid");
		add_to_log($this->course->id, $mod->modname, "add",
		"view.php?id=$mod->id",
				"$instanceid", $mod->id);
		$course_module_data = array('courseid' => $this->course->id,
									'sectionid' => $this->section,
									'cmid' => $this->cm->id);
		return $course_module_data;
	}
	
	public function delete_private_user_file(){
		$fs = get_file_storage();
	
		// Prepare file record object
		$fileinfo = array(
				'component' => $this->filecomponent,
				'filearea' => $this->filearea,
				'itemid' => $this->fileitemid,
				'contextid' => $this->filecontextid,
				'filepath' => $this->filepath,
				'filename' => $this->filename);
			
		// Get file
		$file = $fs->get_file($fileinfo['contextid'], $fileinfo['component'], $fileinfo['filearea'],
				$fileinfo['itemid'], $fileinfo['filepath'], $fileinfo['filename']);
		if ($file) {
			$file->delete();
		}
	}
	
	public function upload(){
		global $USER;
		// check the user can manage his own files (can upload)
		$context = context_user::instance($USER->id);
		require_capability('moodle/user:manageownfiles', $context);
		
		$fs = get_file_storage();
		
		$totalsize = 0;
		$files = array();
		foreach ($_FILES as $fieldname=>$uploaded_file) {
			// check upload errors
			if (!empty($_FILES[$fieldname]['error'])) {
				switch ($_FILES[$fieldname]['error']) {
					case UPLOAD_ERR_INI_SIZE:
						throw new moodle_exception('upload_error_ini_size', 'repository_upload');
						break;
					case UPLOAD_ERR_FORM_SIZE:
						throw new moodle_exception('upload_error_form_size', 'repository_upload');
						break;
					case UPLOAD_ERR_PARTIAL:
						throw new moodle_exception('upload_error_partial', 'repository_upload');
						break;
					case UPLOAD_ERR_NO_FILE:
						throw new moodle_exception('upload_error_no_file', 'repository_upload');
						break;
					case UPLOAD_ERR_NO_TMP_DIR:
						throw new moodle_exception('upload_error_no_tmp_dir', 'repository_upload');
						break;
					case UPLOAD_ERR_CANT_WRITE:
						throw new moodle_exception('upload_error_cant_write', 'repository_upload');
						break;
					case UPLOAD_ERR_EXTENSION:
						throw new moodle_exception('upload_error_extension', 'repository_upload');
						break;
					default:
						throw new moodle_exception('nofile');
				}
			}
			$file = new stdClass();
			$file->filename = clean_param($_FILES[$fieldname]['name'], PARAM_FILE);
			// check system maxbytes setting
			if (($_FILES[$fieldname]['size'] > get_max_upload_file_size($CFG->maxbytes))) {
				// oversize file will be ignored, error added to array to notify
				// web service client
				$file->errortype = 'fileoversized';
				$file->error = get_string('maxbytes', 'error');
			} else {
				$file->filepath = $_FILES[$fieldname]['tmp_name'];
				// calculate total size of upload
				$totalsize += $_FILES[$fieldname]['size'];
			}
			$files[] = $file;
		}
		
		$fs = get_file_storage();
		
		$usedspace = 0;
		$privatefiles = $fs->get_area_files($context->id, 'user', 'private', false, 'id', false);
		
		$results = array();
		foreach ($files as $file) {
			if (!empty($file->error)) {
				// including error and filename
				$results[] = $file;
				continue;
			}
			$file_record = new stdClass;
			$file_record->component = 'user';
			$file_record->contextid = $context->id;
			$file_record->userid    = $USER->id;
			$file_record->filearea  = 'private';
			$file_record->filename = $file->filename;
			$file_record->filepath  = '/';
			$file_record->itemid    = 0;
			$file_record->license   = $CFG->sitedefaultlicense;
			$file_record->author    = fullname($authenticationinfo['user']);;
			$file_record->source    = '';
		
			//Check if the file already exist
			$existingfile = $fs->file_exists($file_record->contextid, $file_record->component, $file_record->filearea,
					$file_record->itemid, $file_record->filepath, $file_record->filename);
			if ($existingfile) {
				$file->errortype = 'filenameexist';
				$file->error = get_string('filenameexist', 'webservice', $file->filename);
				$results[] = $file;
			} else {
				$stored_file = $fs->create_file_from_pathname($file_record, $file->filepath);
				$results[] = $file_record;
			}
		}

		$this->filecontextid = $results[0]->contextid;
		$this->filecomponent = $results[0]->component;
		$this->filearea = $results[0]->filearea;
		$this->fileitemid = $results[0]->itemid;
		$this->filename = $results[0]->filename;
		$this->filepath = $results[0]->filepath;

	}
	
}
