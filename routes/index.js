var express = require('express');
var router = express.Router();
const spawn = require("child_process").spawn;
const PATH = "./predict/model.py"
const {districts, wards, projects, balconyDirections, legalPapers, features} = require('../data/constants');


/* GET home page. */
router.get('/', function (req, res, next) {
  res.render('index', { 
    title: 'Ước lượng giá chung cư',
    districts: districts.sort(),
    wards: wards.sort(),
    projects: projects.sort(),
    balconyDirections,
    legalPapers,
    features
  });
});

/* POST home page. */
router.post('/predict', function (req, res, next) {
  // Get arguments
  const argv = req.body;
  
  const district = argv['district']
  const ward = argv['ward']
  const project = argv['project']
  
  const area = parseFloat(argv['area'])
  if (!argv['bedroom']) {
    var bedroom = '';
  } else {
    var bedroom = parseInt(argv['bedroom'])
  }

  if (!argv['bathroom']) {
    var bathroom = ''
  } else {
    var bathroom = parseInt(argv['bathroom'])
  }

  const pool = argv['pool'] == 'on' ? 'Có' : 'Không'
  const skyview = argv['skyview'] == 'on' ? 'Có' : 'Không'

  const lat = argv['lat']
  const lon = argv['lon']

  const legal = []
  const feature = []
  const balcony = []

  for (const key in argv) {
    if(key.startsWith("LGPP ") && argv[key] == 'on') {
      // Cắt bỏ LGPP rồi push vào legal
      legal.push(key.slice(5));
    }
    
    if(key.startsWith("FT ") && argv[key] == 'on') {
      // Cắt bỏ FT rồi push vào feature
      feature.push(key.slice(3));
    }
    
    if(key.startsWith("DR ") && argv[key] == 'on') {
      // Cắt bỏ DR rồi push vào balcony
      balcony.push(key.slice(3));
    }
  }

  // Argument will be pass to python process
  pyArgs = [PATH, pool, skyview, bedroom, bathroom, area, lat, lon, legal, feature, district, ward, project, balcony]

  console.log(pyArgs);

  // Call python process
  const pythonProcess = spawn('python', pyArgs);

  // Receive data
  pythonProcess.stdout.on('data', function (data) {
    console.log(data.toString());
    res.send(data);
  });

  // If call python fail
  pythonProcess.stderr.on('data', (data) => {
    console.log(data.toString());
  });
});

module.exports = router;

/* Note:
  Ở đây gọi file python, load model lên, thực hiện dự đoán
  Cách này chưa tối ưu, vì trong trường hợp model nặng mà có nhiều request user gửi đến thì sẽ bị chậm
  Bởi vì model phải load liên tục
  Giải pháp thay thế là cần 1 process load sẵn model chạy ngầm liên tục và đợi các request gửi tới thì chỉ
  cần thực hiện predict. 
  Tuy nhiên với phạm vi bài tập lớn môn khoa học dữ liệu, thì như vậy là tạm ổn rồi. 
  Môn học cũng không chú trọng phần xử lý web này.
  */