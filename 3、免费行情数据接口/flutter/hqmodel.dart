class HqModel {
  HqModel({
    this.name,
    this.code,
    this.price,
    this.lastClose,
    this.open,
    this.high,
    this.low,
    this.vol,
    this.volAmount,
    this.date,
    this.time,
    this.change,
    this.changeRatio,
  });
  String? name;
  String? code;
  String? price;
  String? lastClose; // 昨收
  String? open;
  String? high;
  String? low;
  String? vol;
  String? volAmount;
  String? date;
  String? time;
  String? change;
  String? changeRatio;
}
