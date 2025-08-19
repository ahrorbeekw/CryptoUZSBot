import os,asyncio,aiohttp,time,math,unicodedata
from aiogram import Bot,Dispatcher,F,Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command,CommandStart
from aiogram.types import Message,CallbackQuery,InlineKeyboardMarkup,InlineKeyboardButton,InlineQuery,InlineQueryResultArticle,InputTextMessageContent

# .env: set TOKEN=xxxxxxxx

tok=os.getenv('TOKEN')
if not tok: raise SystemExit('TOKEN env is required')

bot=Bot(tok,default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp=Dispatcher()
rt=Router()
dp.include_router(rt)

session=None
usd_uzs=0.0
px={} # key: symbol(lower), value: dict(name,price_usd,price_uzs,rank)
mt=0.0

hdr={'User-Agent':'CryptoUZSBot/1.0'}

async def j(url,params=None,tries=3,timeout=20):
  for i in range(tries):
    try:
      async with session.get(url,params=params,timeout=timeout,headers=hdr) as r:
        if r.status==200:
          return await r.json()
    except Exception:
      await asyncio.sleep(1+0.5*i)
  return None

async def rate_usd_uzs():
  d=await j('https://cbu.uz/uz/arkhiv-kursov-valyut/json/USD/')
  if d and isinstance(d,list) and d[0].get('Rate'):
    return float(d[0]['Rate'])
  d=await j('https://open.er-api.com/v6/latest/USD')
  if d and d.get('result')=='success' and d['rates'].get('UZS'):
    return float(d['rates']['UZS'])
  d=await j('https://api.exchangerate.host/latest',{'base':'USD','symbols':'UZS'})
  if d and d.get('rates') and d['rates'].get('UZS'):
    return float(d['rates']['UZS'])
  return 0.0

async def fetch_coincap(limit=1000):
  out={}
  of=0
  rk=1
  while of<limit:
    d=await j('https://api.coincap.io/v2/assets',{'limit':200,'offset':of})
    if not d or 'data' not in d: break
    it=d['data']
    if not it: break
    for a in it:
      nm=a.get('name','')
      sm=a.get('symbol','')
      p=a.get('priceUsd')
      if not sm or not p: continue
      sm=sm.strip().upper()
      pr=float(p)
      out[sm]={'name':nm,'symbol':sm,'price_usd':pr,'rank':rk}
      rk+=1
    of+=200
  return out

async def fetch_binance_syms():
  d=await j('https://api.binance.com/api/v3/ticker/price')
  out={}
  if not d: return out
  for x in d:
    s=x.get('symbol','')
    if s.endswith('USDT') and len(s)>5:
      sm=s[:-4]
      try:
        out[sm]={'price_usd':float(x['price'])}
      except Exception:
        pass
  return out

async def merge_prices():
  g=await fetch_coincap(1000)
  b=await fetch_binance_syms()
  for s,v in b.items():
    if s in g:
      g[s]['price_usd']=v['price_usd']
    else:
      g[s]={'name':s,'symbol':s,'price_usd':v['price_usd'],'rank':999999}
  return g

def fmt_num(x):
  if x>=1e9: return f"{x/1e9:.2f}B"
  if x>=1e6: return f"{x/1e6:.2f}M"
  if x>=1e3: return f"{x/1e3:.2f}K"
  if x>=1: return f"{x:.2f}"
  d=0
  y=x
  while y<1 and y>0 and d<8:
    y*=10
    d+=1
  d=min(max(d,2),8)
  return f"{x:.{d}f}"

def clean(s):
  return ''.join(c for c in s if not unicodedata.category(c).startswith('C'))

async def rebuild():
  global usd_uzs,px,mt
  r=await rate_usd_uzs()
  if r>0: usd_uzs=r
  m=await merge_prices()
  q={}
  for s,v in m.items():
    pu=v['price_usd']
    pz=pu*usd_uzs if usd_uzs>0 else 0
    q[s.lower()]={'name':v.get('name',s),'symbol':s,'price_usd':pu,'price_uzs':pz,'rank':v.get('rank',999999)}
  if q:
    px=q
    mt=time.time()

async def loop_refresh():
  while True:
    try:
      await rebuild()
    except Exception:
      pass
    await asyncio.sleep(60)

def page(items,pg,ps):
  n=len(items)
  t=max(1,math.ceil(n/ps))
  pg=max(1,min(pg,t))
  a=(pg-1)*ps
  b=min(a+ps,n)
  return items[a:b],pg,t

def kb_pg(q,pg,t):
  l=[]
  if t>1:
    l.append([InlineKeyboardButton(text='⏮️',callback_data=f'p|{q}|1'),InlineKeyboardButton(text='◀️',callback_data=f'p|{q}|{max(1,pg-1)}'),InlineKeyboardButton(text=f'{pg}/{t}',callback_data='noop'),InlineKeyboardButton(text='▶️',callback_data=f'p|{q}|{min(t,pg+1)}'),InlineKeyboardButton(text='⏭️',callback_data=f'p|{q}|{t}')])
  l.append([InlineKeyboardButton(text='🔄 Yangilash',callback_data=f'r|{q}|{pg}')])
  return InlineKeyboardMarkup(inline_keyboard=l)

def row_text(v):
  n=v['name']
  s=v['symbol']
  pu=v['price_usd']
  pz=v['price_uzs']
  return f"<b>{clean(n)}</b> (<code>{s}</code>)\n$ {fmt_num(pu)}\nso'm {fmt_num(pz)}\n"

def list_text(lst,ttl):
  z=[f"<b>{ttl}</b>"]
  for v in lst:
    z.append(f"{v['rank']}. <b>{clean(v['name'])}</b> <code>{v['symbol']}</code> — $ {fmt_num(v['price_usd'])} • so'm {fmt_num(v['price_uzs'])}")
  z.append(f"\nKurs: 1 USD= {fmt_num(usd_uzs)} so'm\nYangilanish: {int(time.time()-mt)} s da")
  return '\n'.join(z)

@rt.message(CommandStart())
async def st(m:Message):
  t="Salom! Bu bot barcha kripto narxlarini O'zbekiston so'mida ko'rsatadi.\n/menu dan foydalaning yoki /top 20"
  await m.answer(t)

@rt.message(Command('menu'))
async def menu(m:Message):
  k=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='TOP 20',callback_data='t|20')],[InlineKeyboardButton(text='TOP 50',callback_data='t|50')],[InlineKeyboardButton(text='Qidirish',callback_data='s|_')]])
  await m.answer('Tanlang:',reply_markup=k)

@rt.callback_query(F.data.startswith('t|'))
async def cb_top(c:CallbackQuery):
  n=int(c.data.split('|')[1])
  it=sorted(px.values(),key=lambda x:x['rank'])[:n]
  p,pg,t=page(it,1,10)
  await c.message.edit_text(list_text(p,f'TOP {n}'),reply_markup=kb_pg(f'top{n}',pg,t))
  await c.answer()

@rt.callback_query(F.data.startswith('p|'))
async def cb_p(c:CallbackQuery):
  _,q,pg=c.data.split('|')
  pg=int(pg)
  if q.startswith('top'):
    n=int(q[3:])
    it=sorted(px.values(),key=lambda x:x['rank'])[:n]
    p,pg,t=page(it,pg,10)
    await c.message.edit_text(list_text(p,f'TOP {n}'),reply_markup=kb_pg(q,pg,t))
  elif q.startswith('s:'):
    s=q[2:]
    it=[v for v in px.values() if s in v['name'].lower() or s in v['symbol'].lower()]
    it=sorted(it,key=lambda x:x['rank'])
    if not it:
      await c.answer('Topilmadi',show_alert=True)
      return
    p,pg,t=page(it,pg,10)
    await c.message.edit_text(list_text(p,f'Natijalar: {s}'),reply_markup=kb_pg(q,pg,t))
  await c.answer()

@rt.callback_query(F.data.startswith('r|'))
async def cb_r(c:CallbackQuery):
  _,q,pg=c.data.split('|')
  await rebuild()
  await cb_p(CallbackQuery(id=c.id,from_user=c.from_user,chat_instance=c.chat_instance,message=c.message,data=f'p|{q}|{pg}'))

@rt.callback_query(F.data.startswith('s|'))
async def cb_s(c:CallbackQuery):
  await c.answer()
  await c.message.answer('Qidiruv so`zini yuboring:')

@rt.message()
async def any_msg(m:Message):
  s=m.text.strip().lower() if m.text else ''
  if s.startswith('/top'):
    try:
      n=int(s.split()[1])
    except Exception:
      n=20
    it=sorted(px.values(),key=lambda x:x['rank'])[:n]
    p,pg,t=page(it,1,10)
    await m.answer(list_text(p,f'TOP {n}'),reply_markup=kb_pg(f'top{n}',pg,t))
    return
  if len(s)>=2:
    it=[v for v in px.values() if s in v['name'].lower() or s in v['symbol'].lower()]
    it=sorted(it,key=lambda x:x['rank'])
    if it:
      p,pg,t=page(it,1,10)
      await m.answer(list_text(p,f'Natijalar: {s}'),reply_markup=kb_pg(f's:{s}',pg,t))
      return
  await m.answer('Buyruqlar: /menu, /top 20, matn yuboring(qidiruv)')

@rt.inline_query()
async def iq(q:InlineQuery):
  s=(q.query or '').strip().lower()
  r=[]
  if len(s)>=2:
    it=[v for v in px.values() if s in v['name'].lower() or s in v['symbol'].lower()]
    it=sorted(it,key=lambda x:x['rank'])[:50]
    for i,v in enumerate(it):
      txt=row_text(v)
      r.append(InlineQueryResultArticle(id=str(i+1),title=f"{v['name']} ({v['symbol']})",description=f"$ {fmt_num(v['price_usd'])} • so'm {fmt_num(v['price_uzs'])}",input_message_content=InputTextMessageContent(message_text=txt,parse_mode='HTML')))
  await bot.answer_inline_query(q.id,results=r,is_personal=True,cache_time=15)

async def main():
  global session
  session=aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30),connector=aiohttp.TCPConnector(limit=50,ssl=False))
  try:
    await rebuild()
    asyncio.create_task(loop_refresh())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
  finally:
    await session.close()

if __name__=='__main__':
  asyncio.run(main())
