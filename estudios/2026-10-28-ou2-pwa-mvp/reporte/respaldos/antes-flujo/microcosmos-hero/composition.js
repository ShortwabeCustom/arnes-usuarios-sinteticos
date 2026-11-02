/* Decorative stories. These figures do not represent the research sample. */
(() => {
 const people = [
  {id:'reader', x:153,y:154, family:'coat', pose:'phone', fill:'blue', story:'quiet', role:'reader', mobile:[120,100]},
  {id:'friend', facing:-1, x:191,y:159, family:'dress', pose:'rest', fill:'paper'},
  {id:'passer', x:108,y:189, family:'cap', pose:'bag', fill:'sage'},
  {id:'sharer', x:500,y:181, family:'jacket', pose:'show', fill:'blue', story:'shared', role:'show', mobile:[290,105]},
  {id:'companion', facing:-1, x:527,y:181, family:'long', pose:'listen', fill:'paper', story:'shared', role:'lean', mobile:[316,108]},
  {id:'observer', x:583,y:205, family:'skirt', pose:'rest', fill:'sage'},
  {id:'walker', x:173,y:325, family:'knit', pose:'walk', fill:'paper', story:'walk', role:'walk', mobile:[85,200]},
  {id:'gardener', x:108,y:382, family:'short', pose:'rest', fill:'blue'},
  {id:'visitor', x:243,y:347, family:'long', pose:'phone', fill:'sage'},
  {id:'seated', x:551,y:366, family:'cap', pose:'seated', fill:'blue', story:'pause', role:'foot', mobile:[340,237]},
  {id:'seated-friend', x:583,y:375, family:'dress', pose:'seated', fill:'paper'},
  {id:'bench-visitor', x:628,y:364, family:'coat', pose:'rest', fill:'sage'},
  {id:'picnic-one', x:253,y:499, family:'short', pose:'sit', fill:'blue'},
  {id:'picnic-two', x:284,y:516, family:'dress', pose:'sit', fill:'paper'},
  {id:'picnic-three', facing:-1, x:310,y:498, family:'knit', pose:'sit', fill:'sage'},
  {id:'picnic-four', x:280,y:475, family:'cap', pose:'rest', fill:'paper'},
  {id:'greeter', x:440,y:482, family:'jacket', pose:'greet', fill:'paper', story:'encounter', role:'wave', mobile:[234,246]},
  {id:'arriving', facing:-1, x:492,y:499, family:'skirt', pose:'walk', fill:'blue', story:'encounter', role:'arrive'},
  {id:'stroller', x:665,y:470, family:'long', pose:'bag', fill:'paper'},
  {id:'quiet-neighbour', x:375,y:111, family:'cap', pose:'rest', fill:'sage'},
 ];
 const slots = [
  {name:'quiet',start:1,duration:3},
  {name:'shared',start:6,duration:5},
  {name:'walk',start:14,duration:7},
  {name:'pause',start:24,duration:3},
  {name:'encounter',start:30,duration:6},
  {name:'shared',start:40,duration:5},
 ];
 // One action at a time. Desktop routes return while fully occluded by shrubs.
 window.MicrocosmosConfig={people,slots,cycle:48,walk:[76,-18],arrive:[-22,-7],mobileWalk:[36,-9],viewBox:[0,0,760,600],mobileViewBox:[0,0,440,280]};
})();
