<?php

namespace App;

/**
 * SQLite connnection
 */
class SQLiteConnection
{
    /**
     * PDO instance
     * @var type
     */
    private $pdo;

    /**
     * return in instance of the PDO object that connects to the SQLite database
     * @return \PDO
     */
    public function connect()
    {
        if ($this->pdo == null) {
            $this->pdo = new \PDO("sqlite:chatbot.db");
        }
        return $this->pdo;
    }
}
