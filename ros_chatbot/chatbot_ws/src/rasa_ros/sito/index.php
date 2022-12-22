<?php
require 'SQLiteConnection.php';

use App\SQLiteConnection;

$pdo = (new SQLiteConnection())->connect();
if ($pdo == null)
  echo 'Whoops, could not connect to the SQLite database!';

$query = 'SELECT user FROM ToDoList ORDER BY user ASC';
$stmt = $pdo->query($query);
$user = [];
while ($row = $stmt->fetch(\PDO::FETCH_ASSOC)) {
  $user[] = [
    'user' => $row['user'],
  ];
}


$numUser = count($user);
?>

<!DOCTYPE html>

<style>
  .center {
    margin: 0;
    position: absolute;
    top: 50%;
    left: 50%;
    -ms-transform: translate(-50%, -50%);
    transform: translate(-50%, -50%);
  }
</style>

<html lang="en">

<head>
  <title>TO-DO LIST</title>
  <meta charset="utf-8" />
  <meta http-equiv="refresh" content="30">
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link href="./bootstrap.min.css" rel="stylesheet" />
  <script src="./bootstrap.bundle.min.js"></script>
  <script src="script.js"></script>
</head>

<body>
  <div class="container mt-3" style="text-align:center">
    <div class="center">
      <h2>Hi, what's your name?</h2>
      <h3>I remember that I interacted with:</h3>
      <ul class="list-group">
        <?php for ($i = 0; $i < $numUser; $i++) { ?>
          <li class="list-group-item"><?php echo ($user[$i]['user']) ?></li>
        <?php } ?>
      </ul>
    </div>
  </div>
</body>

</html>