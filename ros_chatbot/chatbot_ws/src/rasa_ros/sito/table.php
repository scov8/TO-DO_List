<?php

require 'SQLiteConnection.php';

use App\SQLiteConnection;

$pdo = (new SQLiteConnection())->connect();
if ($pdo == null)
  echo 'Whoops, could not connect to the SQLite database!';

if (!isset($_GET["username"]))
  header("location: ./index.php");
$username = $_GET["username"];


$query = 'SELECT task, time, category, reminder ' . 'FROM ToDoList ' . 'WHERE user="' . $username . '" ' . 'ORDER BY time ASC';
$stmt = $pdo->query($query);
$tasks = [];
while ($row = $stmt->fetch(\PDO::FETCH_ASSOC)) {
  $tasks[] = [
    'task' => $row['task'],
    'time' => $row['time'],
    'category' => $row['category'],
    'reminder' => $row['reminder']
  ];
}

$numTasks = count($tasks);

?>

<!DOCTYPE html>
<html lang="en">

<head>
  <title>TO-DO LIST</title>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link href="./bootstrap.min.css" rel="stylesheet" />
  <script type="text/javascript">
    function goToUser(user) {
      window.location.href = "http://10.0.1.213:80/sito/table.php/?username=" + user;
    }

    function refresh() {
      location.reload();
    }
  </script>
  <script src="./bootstrap.bundle.min.js"></script>
  <script>
    function reload() {
      location.reload();
    }

    function refresh() {
      var d = new Date();
      var s = d.getSeconds();
      if (s == 0) {
        setTimeout(function() {
          location.reload()
        }, 1000 * (60 - d.getSeconds()));
      };
    }
  </script>
</head>

<body onload="refresh(), setInterval('refresh()',1)">
  <div class="container mt-3">
    <h2>Hi, <?php echo ($username) ?></h2>
    <?php if ($numTasks == 0) { ?>
      <h3>Nice to meet you</h3>
    <?php } else { ?>
      <p>This is your TO-DO LIST:</p>
      <table class="table table-hover">
        <thead>
          <tr>
            <th>Task</th>
            <th>Date and Time</th>
            <th>Category</th>
            <th>Reminder</th>
          </tr>
        </thead>
        <tbody>
          <?php for ($i = 0; $i < $numTasks; $i++) { ?>
            <tr>
              <td><?php echo ($tasks[$i]['task']) ?></td>
              <td><?php echo (date_format(date_create($tasks[$i]['time']), "d/m/Y H:i:s")) ?></td>
              <td><?php echo ($tasks[$i]['category']) ?></td>
              <td><?php echo ($tasks[$i]['reminder']) ?></td>
              <?php if (date_format(date_create($tasks[$i]['time']), "d/m/Y H:i") <= date("d/m/Y h:i", strtotime("+1 Hour"))) {
                $query = 'DELETE FROM ToDoList ' . 'WHERE task="' . $tasks[$i]['task'] . '" AND user= "' . $username . '"';
                $stmt = $pdo->query($query);
                if ($tasks[$i]['reminder'] == "true" or $tasks[$i]['reminder'] == 1) {
                  $message = $tasks[$i]['task'];
                  echo "<script type='text/javascript'>alert('$message');</script>";
                }
              }
              ?>
            </tr>
          <?php } ?>
        </tbody>
      </table>
    <?php } ?>
  </div>
</body>

</html>