const K=require("../web/detector.js"), A=require("../web/ask.js"), D=require("../web/rules.json");
const cases=[
 ["I gave my PIN to someone who called","shared_pin","en"],
 ["How do I make a strong password?","strong_passwords","en"],
 ["Someone says they sent money by mistake","mistaken_transfer","en"],
 ["j'ai perdu mon téléphone","lost_phone","fr"],
 ["Natanze kode ya WhatsApp","shared_pin|whatsapp_hijack","rw"],
 ["Nimepoteza simu yangu","lost_phone","sw"],
 ["Where do I report a scam?","where_to_report","en"],
 ["Is public wifi safe?","public_wifi","en"],
 ["Tell me a recipe for pilau",null,"en"],
 ["Who won the world cup?",null,"en"],
 ["What is the capital of France?",null,"en"],
 ["Une vérification en deux étapes, c'est quoi ?","two_step","fr"],
 ["ndafite ubutumwa buvuga ko nsabwa kwishyura viza","job_visa_scam","rw"],
 ["Nawezaje kuepuka programu bandia","fake_apps","sw"],

 ["I gave my PIN to someone who called","shared_pin","rw"],
 ["How do I write a CV?","write_cv","en"],
 ["How do I calculate 20 percent of a number","math_percentage","en"],
 ["why do my tomatoes rot after harvest","post_harvest_fresh","en"],
 ["How should I store maize safely","grain_storage","en"],
 ["How can I make drinking water safe","clean_water","en"],
 ["How do I start learning programming","learn_programming","en"],
 ["What is artificial intelligence?","what_is_ai","en"],
 ["Comment calculer un pourcentage ?","math_percentage","fr"],
 ["Nawezaje kuanzisha biashara ndogo","start_business","sw"],
 ["Nakwiga nte neza","study_tips","rw"],
 ["Capital of Rwanda","rwanda_basics","en"],
 ["What is the best football team",null,"en"],
 ["solve x squared plus 3x equals 10",null,"en"],
];
let bad=0;
for(const [q,exp,l] of cases){const b=A.best(A.search(K,D.guide,q,l));const id=b?b.entry.id:null;
 const ok=exp===null?id===null:exp.split("|").includes(id); if(!ok){bad++;console.log("FAIL",q,"->",id,"expected",exp);}}
console.log(bad?bad+" failed":"ask retrieval ok ("+cases.length+")");process.exit(bad?1:0);
