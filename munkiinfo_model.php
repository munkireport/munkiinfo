<?php

use CFPropertyList\CFPropertyList;

class Munkiinfo_model extends \Model
{
    public function __construct($serial = '')
    {
          parent::__construct('id', 'munkiinfo'); //primary key, tablename
          $this->rs['id'] = "";
          $this->rs['serial_number'] = $serial;
          $this->rs['munkiinfo_key'] = '';
          $this->rs['munkiinfo_value'] = '';

        if ($serial) {
            $this->retrieve_record($serial);
          
            $this->serial = $serial;
        }
    }

  /**
   * Process data sent by postflight
   *
   * @param string data
   * @author erikng
   **/
    public function process($data)
    {
        // Parse plist or YAML data
        $trimmedData = ltrim($data);
        if (strpos($trimmedData, '<?xml') === 0 ||
            strpos($trimmedData, '<!DOCTYPE plist') !== false ||
            strpos($trimmedData, '<plist') !== false) {
            $parser = new CFPropertyList();
            $parser->parse($data, CFPropertyList::FORMAT_XML);
            $parsedData = $parser->toArray();
        } else {
            $parsedData = \Symfony\Component\Yaml\Yaml::parse($data);
        }

        if (!$parsedData) {
            return;
        }

        $this->deleteWhere('serial_number=?', $this->serial_number);
        $item = array_pop($parsedData);
        if (!$item || !is_array($item)) {
            return;
        }
        reset($item);
        foreach($item as $key => $val) {
                $this->munkiinfo_key = $key;
                $this->munkiinfo_value = $val;

                $this->id = '';
                $this->save();
        }
    }
}
