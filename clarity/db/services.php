<?php

/**
 * Clarity Web service local plugin external functions and service definitions.
 *
 * @package    local/clarity
 */

// We defined the web service functions to install.
$functions = array(
        'local_clarity_create_resource' => array(
                'classname'   => 'local_clarity_external',
                'methodname'  => 'create_resource',
                'classpath'   => 'local/clarity/externallib.php',
                'description' => 'Creates a resource.',
                'type'        => 'write',
        )
);

// We define the services to install as pre-build services. A pre-build service is not editable by administrator.
$services = array(
        'Clarity' => array(
                'functions' => array ('local_clarity_create_resource'),
                'restrictedusers' => 0,
                'enabled'=>1,
        )
);
