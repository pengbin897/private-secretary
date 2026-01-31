''' 标书助理 '''
import os, requests, logging
import pandas as pd
import urllib.parse
from bs4 import BeautifulSoup

from agentscope.agent import ReActAgent
from agentscope.model import DashScopeChatModel
from agentscope.formatter import DashScopeChatFormatter


logger = logging.getLogger(__name__)

data = """
链接,标题,日期
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?type=article&id=e6fe8095-bc2c-42b0-a344-3cca74d9aed0&channelName=%E7%94%B5%E5%AD%90%E5%8D%96%E5%9C%BA%E5%85%AC%E5%91%8A,广东省教育厅审计服务定点服务定点议价采购合同,2025/12/23
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=6f7781cb-e8e7-4d94-82a4-584aa3909635&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=GDJY251013001FG046&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育厅2025年广东省学生体质健康抽测项目的合同公告,2025/12/19
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=df970bc7-971b-4788-b5e5-39f195c97b41&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=GDJY251013001FG046&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育厅2025年广东省学生体质健康抽测项目的合同公告,2025/12/19
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=4d3479e6-f605-4593-8173-afd5f79b4c1a&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=GDJY251013001FG046&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育厅2025年广东省学生体质健康抽测项目的合同公告,2025/12/19
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?type=article&id=2516c4a1-c5dd-4277-bfcb-83830dc43dd7&channelName=%E7%94%B5%E5%AD%90%E5%8D%96%E5%9C%BA%E5%85%AC%E5%91%8A,广东省教育厅审计服务电子卖场合同的合同公告,2025/12/13
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?type=article&id=9c1afe12-b0e9-432c-b3fd-14b63e247b2e&channelName=%E7%94%B5%E5%AD%90%E5%8D%96%E5%9C%BA%E5%85%AC%E5%91%8A,广东省教育厅审计服务定点议价采购公告,2025/12/11
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?id=4b4b9aae-64cd-4a87-b73c-9dafdec54f06&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育厅事务中心（广东省电化教育馆）2025年12月政府采购意向,2025/12/10
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?type=article&id=449f9e33-3e11-4bac-a50a-e9f880b8fcf0&channelName=%E7%94%B5%E5%AD%90%E5%8D%96%E5%9C%BA%E5%85%AC%E5%91%8A,广东省教育厅事务中心（广东省电化教育馆）法律服务定点议价采购公告,2025/12/5
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?type=article&id=b34f4035-875f-4fd3-bf32-202cb9f05b17&channelName=%E7%94%B5%E5%AD%90%E5%8D%96%E5%9C%BA%E5%85%AC%E5%91%8A,广东省教育厅事务中心（广东省电化教育馆）法律服务定点采购定点议价成交公告,2025/12/5
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?type=article&id=3f7a74f7-90e6-45ff-8961-6c7337f69e3d&channelName=%E7%94%B5%E5%AD%90%E5%8D%96%E5%9C%BA%E5%85%AC%E5%91%8A,广东省教育厅审计服务电子卖场合同的合同公告,2025/12/4
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?id=4fa85683-fb48-4fc2-a221-e83d3cef7797&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育厅事务中心（广东省电化教育馆）2025年12月政府采购意向,2025/12/4
https://gdgpo.czt.gd.gov.cn/maincms-web/articleRedHeadGd?id=fbf80756-9b33-494f-b63c-5eb1dbeba154&channelName=%E9%87%87%E8%B4%AD%E8%AE%A1%E5%88%92%E6%A8%A1%E6%9D%BF,广东省教育厅事务中心（广东省电化教育馆）法律顾问服务项目,2025/12/4
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?type=article&id=75d2dd83-2fd1-4677-b3da-9f8b05a5285b&channelName=%E7%94%B5%E5%AD%90%E5%8D%96%E5%9C%BA%E5%85%AC%E5%91%8A,广东省教育厅审计服务定点议价采购公告,2025/12/2
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?type=article&id=56e585fc-52cd-4660-a4c7-91d9b35ec06b&channelName=%E7%94%B5%E5%AD%90%E5%8D%96%E5%9C%BA%E5%85%AC%E5%91%8A,广东省教育厅审计服务定点采购定点议价成交公告,2025/12/2
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=334d1aab-dba1-4582-a544-e5da11e702ec&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=GDJY251013001FG046&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,2025年广东省学生体质健康抽测项目 [项目编号：GDJY251013001FG046]结果公告,2025/11/25
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=1bf3535f-e79a-4c9c-a633-ba8f95ace25e&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=4188-2541GDG32711&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育专网服务（2025年）项目（二次）结果公告,2025/11/20
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?id=3db751ef-8431-42ac-a02e-61be8722c5f0&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育厅事务中心（广东省电化教育馆）2025年11月政府采购意向,2025/11/12
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=53cf2bfe-e51b-42a9-8abb-e8dc6b1a28d5&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=GPCGD251156FG300F&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,省教育厅安全服务（2025年）项目结果公告,2025/11/7
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=790629ed-6e17-4792-83f4-f221708e3351&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=GDJY251013001FG046&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,2025年广东省学生体质健康抽测项目 [项目编号：GDJY251013001FG046]采购更正公告（第一次）,2025/11/6
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=56a08469-34e7-44bf-824f-ddca9cbe3509&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=GPCGD251156FG301F&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,省教育厅政务信息化运维服务（2025年）项目结果公告,2025/10/30
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=79280351-254a-4103-91f0-13b739970322&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=4188-2541GDG32711&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育专网服务（2025年）项目(二次)招标公告,2025/10/24
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=ebf51db8-c29a-4276-8681-085e83079453&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=4188-2541GDG32711&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育专网服务（2025年）项目招标失败公告,2025/10/18
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=232eb4aa-426a-44cc-9c7c-e9e686ca8569&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=GDJY251013001FG046&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,2025年广东省学生体质健康抽测项目[项目编号：GDJY251013001FG046]招标公告,2025/10/17
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=d454aeed-b516-4aae-a6c4-e6bcbc7c8d67&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=GDJY250320004FG006&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育厅广东省校园安全管理中心日常保障服务项目的合同公告,2025/10/16
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=971c21d3-21bb-47ee-870b-1ddd12fdc18e&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=GPCGD251156FG300F&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,省教育厅安全服务（2025年）项目招标公告,2025/10/14
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=971c21d3-21bb-47ee-870b-1ddd12fdc18e&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=GPCGD251156FG300F&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,省教育厅安全服务（2025年）项目招标公告,2025/10/14
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=e7b0b8fd-9f31-4e95-a69e-e15978435f30&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=GPCGD251156FG301F&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,省教育厅政务信息化运维服务（2025年）项目采购更正公告（第一次）,2025/10/12
https://gdgpo.czt.gd.gov.cn/maincms-web/articleRedHeadGd?id=c033e2a6-4d65-44f0-b770-8e437fe569e1&channelName=%E9%87%87%E8%B4%AD%E8%AE%A1%E5%88%92%E6%A8%A1%E6%9D%BF,广东省教育厅教育科研网接入服务（2025年）项目,2025/10/1
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=5e456046-1b31-4592-8b0d-69ccdac43d94&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=4188-2541GDG32711&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育专网服务（2025年）项目招标公告,2025/9/27
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=b888a841-76d1-42f1-a49b-921a75f5c709&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=GPCGD251156FG301F&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,省教育厅政务信息化运维服务（2025年）项目招标公告,2025/9/27
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?type=article&id=fb8ec162-45af-4595-bcd6-2b6a87cb8800&channelName=%E7%94%B5%E5%AD%90%E5%8D%96%E5%9C%BA%E5%85%AC%E5%91%8A,广东省教育厅事务中心（广东省电化教育馆）互联网接入服务定点议价采购公告,2025/9/27
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?id=a4997630-8808-4898-a1ae-89ccd2d171c1&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育厅事务中心（广东省电化教育馆）2025年09月政府采购意向,2025/9/20
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?id=53c94928-378a-4acf-8e10-e890a1a03ea2&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育厅事务中心（广东省电化教育馆）2025年09月政府采购意向,2025/9/18
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?id=14cd7235-951c-420a-b216-daa9e07d600d&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育厅事务中心（广东省电化教育馆）2025年09月政府采购意向,2025/9/18
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?id=42afefe1-1783-4f75-a0b1-bcd6c1c23001&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育厅2025年09月至2025年10月政府采购意向,2025/9/13
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?type=article&id=3282d2f2-fd8e-4616-a5b1-2b4384062317&channelName=%E7%94%B5%E5%AD%90%E5%8D%96%E5%9C%BA%E5%85%AC%E5%91%8A,广东省教育厅审计服务电子卖场合同的合同公告,2025/9/4
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?type=article&id=215d2ad5-2d21-4c5a-9bd8-e391b050bc3c&channelName=%E7%94%B5%E5%AD%90%E5%8D%96%E5%9C%BA%E5%85%AC%E5%91%8A,广东省教育厅审计服务定点采购定点议价成交公告,2025/9/3
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?id=eb136eec-9ddb-4fdd-ae84-03d723b7cd1b&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育厅2025年08月至2025年09月政府采购意向,2025/8/22
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?id=f9db3005-cbf6-4adc-93fe-eecf66181764&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育厅事务中心（广东省电化教育馆）2025年08月政府采购意向,2025/8/22
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=09ba9b44-7594-413b-b4ac-7fe2d4df1047&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=GDJY250320004FG006&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省校园安全管理中心日常保障服务项目【项目编号：GDJY250320004FG006】结果公告,2025/8/22
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?type=article&id=e63c1269-9691-4b35-9ecc-c7a9c8904591&channelName=%E7%94%B5%E5%AD%90%E5%8D%96%E5%9C%BA%E5%85%AC%E5%91%8A,广东省教育厅审计服务电子卖场合同的合同公告,2025/8/15
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?type=article&id=6b898f33-dcf6-4f14-93c5-30db0fcd9c9f&channelName=%E7%94%B5%E5%AD%90%E5%8D%96%E5%9C%BA%E5%85%AC%E5%91%8A,广东省教育厅审计服务定点议价采购公告,2025/8/13
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?id=f05c2f3c-b817-453d-8496-1810bc40f530&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育厅事务中心（广东省电化教育馆）2025年07月至2025年08月政府采购意向,2025/7/29
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=8e12ca1a-4366-41c6-88ac-43305889bdf1&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=GDJY250320004FG006&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省校园安全管理中心日常保障服务项目 [采购项目编号：GDJY250320004FG006]招标公告,2025/7/29
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?type=article&id=c5961c1d-6603-4f4d-9502-30c96147d9dd&channelName=%E7%94%B5%E5%AD%90%E5%8D%96%E5%9C%BA%E5%85%AC%E5%91%8A,广东省教育厅审计服务定点采购定点议价成交公告,2025/7/29
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?type=article&id=c5961c1d-6603-4f4d-9502-30c96147d9dd&channelName=%E7%94%B5%E5%AD%90%E5%8D%96%E5%9C%BA%E5%85%AC%E5%91%8A,广东省教育厅审计服务定点采购定点议价成交公告,2025/7/29
https://gdgpo.czt.gd.gov.cn/maincms-web/noticeGd?type=notice&id=b0ce5bd7-9953-4603-a4cb-2e81c7371996&channel=fca71be5-fc0c-45db-96af-f513e9abda9d&openTenderCode=GDJY250307001FD004&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育厅硕士学位论文抽检通讯评审服务的合同公告,2025/7/25
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?id=602d3bb9-e49b-47c2-846a-db8253427506&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育厅事务中心（广东省电化教育馆）2025年07月至2025年09月政府采购意向,2025/7/18
https://gdgpo.czt.gd.gov.cn/maincms-web/articleGd?id=d2a0c670-c9e7-4b07-81e3-54f102bdec3b&channelName=%E9%87%87%E8%B4%AD%E9%A1%B9%E7%9B%AE%E4%BF%A1%E6%81%AF,广东省教育厅事务中心（广东省电化教育馆）2025年07月政府采购意向,2025/7/12
https://edu.gd.gov.cn/zwgknew/zbcg/content/post_4513018.html,评标专家和评标专家库管理办法,2024/10/28
https://edu.gd.gov.cn/zwgknew/zbcg/content/post_4439192.html,综合比选采购结果公告,2024/6/12
https://edu.gd.gov.cn/zwgknew/zbcg/content/post_4436912.html,2024年“暑假安全宣传教育周”启动仪式项目综合比选采购公告,2024/6/6
https://edu.gd.gov.cn/zwgknew/zbcg/content/post_3451398.html,广东省教育厅印发《广东省教育厅关于省直教育系统政府采购负面清单》的通知,2021/8/4
"""
prompt = """
你是一个招标助手，擅长分析采购意向通知的内容。
"""

agent = ReActAgent(
    name="招标助手",
    model=DashScopeChatModel(
        "qwen3-max-preview",
        api_key="sk-90cb7ca9e5de40dd813756824f0d5fab",
        stream=True,
    ),
    sys_prompt=prompt,
    formatter=DashScopeChatFormatter(),
)

def agent_main(user_id: str, user_message: str, reply_hook: callable):
    # 模拟爬取发布的数据
    df = pd.read_csv(data)

    for artical_url, title, date in df.values:
        # 对于采购意向进行分析解读
        if '意向' in title or '招标公告' in title:
            reply_hook(f"开始对《{title}》进行分析解读...")
            url_parts = artical_url.split('?')
            if len(url_parts) > 1:
                # 将artical_url中的参数解析出来
                url_params = urllib.parse.parse_qs(url_parts[1])
                content_id = url_params['id'][0]

            if not content_id:
                print(f"无法获取《{title}》的内容ID，跳过...")
                continue
            
            response = requests.get(f"https://gdgpo.czt.gd.gov.cn/gpcms/rest/web/v2/info/getInfoById?id={content_id}")
            if response.status_code != 200:
                logger.warning(f"无法获取《{title}》的内容，跳过...")
                continue
            # 提取到content内容
            content = response.json()['data']['content']
            # 提取到content中的所有html标签
            content_html = BeautifulSoup(content, 'html.parser')
            # 获取<div class="noticeArea">标签内的内容
            main_content = content_html.find('div', class_='noticeArea')
            
            # 对内容进行分析

