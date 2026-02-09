톰캣 자체 세션 클러스터링은 “WAS들이 서로 세션을 복제·동기화”하는 방식이고, IMDG 기반 세션 클러스터링은 “외부 분산 메모리 그리드에 세션을 저장”하고 모든 WAS가 거기에 붙는 방식입니다.[1][2][3][4]

## 1. 톰캣 WAS 세션 클러스터링 원리

- 각 톰캣 인스턴스가 클러스터에 참여하고, 세션이 생성·변경될 때 다른 노드로 세션 데이터를 전파합니다.[5][6][1]
- DeltaManager(모든 노드에 복제) 또는 BackupManager(특정 백업 노드에만 복제) 같은 Session Manager를 사용해 복제 범위를 제어합니다.[6][7][8]
- 새로운 노드가 클러스터에 합류할 때 기존 노드에서 세션 상태를 한 번에 받아온 뒤 서비스 요청을 받기 시작합니다.[1][5]
- 주로 멀티캐스트/유니캐스트 기반의 내부 통신 채널(Delta 전파, heartbeat 등)을 사용하며, 세션은 각 톰캣의 JVM 메모리에 존재합니다.[9][10][5][1]

### 톰캣 세션 클러스터링 장점

- 애플리케이션 코드 수정 없이, web.xml에 distributable 설정 및 server.xml 클러스터 설정만으로 사용할 수 있습니다.[11][9][1]
- 세션이 각 WAS 메모리에 있으므로, 네트워크 홉이 짧고 지연이 상대적으로 작습니다(소규모 클러스터 기준).[8][6][1]
- 톰캣 생태계 문서/사례가 많아 운영 난이도 초반 진입 장벽이 낮습니다.[7][11][1]

### 톰캣 세션 클러스터링 단점

- 노드 수가 늘수록 세션 복제 트래픽이 기하급수적으로 증가하고, 성능·스케일링에 한계가 있습니다.[6][7][8]
- 각 JVM 메모리에 세션을 들고 있어 힙 사용량이 커지고, GC 부담 및 OutOfMemory 리스크가 증가합니다.[12][8][6]
- 세션 관리가 WAS 라이프사이클과 강하게 결합되어, 톰캣 롤링 배포·버전 혼재 시 구성·호환성 이슈가 발생할 수 있습니다.[13][9][1]

예: 3대 톰캣, DeltaManager 사용 시 로그인 세션 변경이 있을 때마다 3대 모두에 변경 내용이 전파되어, 고트래픽 환경에서는 네트워크와 CPU 오버헤드가 상당히 커집니다.[7][8][6]

## 2. IMDG 세션 클러스터링 원리

- In-Memory Data Grid(예: Infinispan, Oracle Coherence 등)에 HTTP 세션을 키-값 형태로 저장합니다.[2][3][14]
- 각 WAS는 로컬 세션 저장소 대신 IMDG 클러스터를 세션 저장소로 사용하며, 세션 생성·조회·갱신 시 IMDG 노드와 통신합니다.[3][14][2]
- IMDG는 자체적으로 파티셔닝, 복제, 장애 감지, 재밸런싱을 수행하여, 세션을 여러 노드에 분산 저장하고 장애 시 다른 노드에서 데이터를 복구합니다.[4][2][3]
- 애플리케이션 서버(WAS)와 IMDG는 논리적으로 분리되어, 여러 종류의 WAS 혹은 여러 애플리케이션이 동일한 세션 그리드를 공유할 수도 있습니다.[14][2][3]

### IMDG 세션 클러스터링 장점

- 세션 데이터가 전용 분산 메모리 계층에 있기 때문에, WAS 수가 늘어나도 세션 복제 오버헤드는 IMDG 쪽에서 흡수되며 선형에 가까운 확장성을 목표로 할 수 있습니다.[2][3][4]
- 세션 관리가 WAS에서 분리되므로, 롤링 배포·노드 교체·스케일아웃 시 세션 유실 없이 유연하게 운영할 수 있습니다.[3][14][2]
- 다중 사이트, 액티브-액티브 구조 등 보다 복잡한 토폴로지에서 세션 고가용성 설계를 지원하는 제품도 많습니다.[4][14][3]
- 세션 외에도 캐시, 공유 상태, 기타 도메인 데이터를 같은 그리드에 올려 재사용 가능해, 아키텍처 단순화와 성능 최적화에 유리합니다.[2][3]

### IMDG 세션 클러스터링 단점

- 별도의 IMDG 클러스터 구축, 운영, 모니터링이 필요해 인프라와 운영 복잡도가 증가합니다.[14][3][2]
- 네트워크를 한 번 더 거쳐야 하므로, 단일 JVM 내 세션 접근보다 지연이 증가할 수 있고, 네트워크 품질에 민감합니다.[12][3][2]
- 상용 IMDG(또는 엔터프라이즈 기능)를 사용할 경우 라이선스 비용이 발생할 수 있으며, 제품별 튜닝 포인트를 이해해야 합니다.[3][14]

예: Coherence*Web을 사용하면 WAS 노드를 교체하거나 다른 사이트로 트래픽을 넘겨도 동일한 IMDG에 붙기만 하면 세션이 유지됩니다.[14][3]

## 3. 톰캣 vs IMDG 세션 클러스터링 비교

### 구조·아키텍처 관점

| 항목 | 톰캣 세션 클러스터링 | IMDG 세션 클러스터링 |
| --- | --- | --- |
| 세션 저장 위치 | 각 톰캣 JVM 메모리[1][7] | IMDG 클러스터(별도 프로세스/노드) 메모리[2][3] |
| 복제 방식 | 톰캣 노드 간 직접 전파 (멀티/유니캐스트)[1][5][6] | IMDG 내부 파티션·복제 메커니즘에 의해 관리[2][3][4] |
| WAS와의 결합도 | WAS와 강결합 (톰캣 기능)[1][9] | 느슨한 결합, 여러 WAS/앱 공유 가능[2][3][14] |
| 구성 복잡도 | 소규모 환경에서는 설정 비교적 단순[1][11][7] | IMDG 설치·클러스터 구성 필요, 상대적으로 복잡[2][3][14] |

### 성능·확장성 관점

| 항목 | 톰캣 세션 클러스터링 | IMDG 세션 클러스터링 |
| --- | --- | --- |
| 노드 확장성 | 노드 수 증가 시 복제 트래픽 급증, 3~4대 이후 비효율 커짐[7][8][6] | IMDG 스케일아웃으로 세션 처리량 수평 확장 가능[2][3][4] |
| 세션 접근 레이턴시 | 로컬 메모리 접근 위주, 상대적으로 짧음[1][8] | 네트워크 I/O 포함, 튜닝/토폴로지에 따라 변동[2][3][12] |
| JVM 메모리 부담 | 세션이 각 WAS에 상주, 힙·GC 부담 큼[8][6][12] | 세션 메모리는 IMDG에 집중, WAS는 상대적으로 가벼움[2][3] |

### 운영·장애 대응 관점

| 항목 | 톰캣 세션 클러스터링 | IMDG 세션 클러스터링 |
| --- | --- | --- |
| 장애 시 세션 보존 | 특정 노드 장애 시 다른 노드에 복제된 세션으로 처리[1][5][6] | IMDG 노드 장애 시 다른 파티션/복제 노드로 자동 재배치[2][3][4] |
| 롤링 배포 | 동일 버전·설정 유지가 중요, 클러스터 호환성 신경 필요[1][9][13] | 세션 계층이 분리되어 있어 WAS 롤링 배포 유연[2][3][14] |
| 모니터링·튜닝 | WAS 모니터링에 포함, 세션 복제 트래픽/GC 관찰[1][7][8] | IMDG 전용 모니터링 및 파티션/복제/TTL 튜닝 필요[2][3][14] |

## 4. 어떤 상황에 무엇을 쓸지 (실무 관점)

- 소규모/중간 규모, 2~3대 톰캣, 내부 서비스, 세션 크기 작고 트래픽이 아주 크지 않음  
  - 톰캣 자체 세션 클러스터링 + 필요하면 sticky session 조합이 구현·운영 비용 대비 효율적입니다.[11][6][7]
- 대규모 트래픽, 다수의 WAS 노드(마이크로서비스, 멀티 DC, 금융 서비스 등), 롤링 배포와 무중단이 중요한 환경  
  - IMDG(또는 Redis 같은 외부 세션 스토어)를 활용한 세션 중앙화가 확장성과 안정성 측면에서 더 적합합니다.[4][12][2][3]

금융권처럼 타임크리티컬· HA 요구가 강하고 배포도 잦은 환경이라면, 톰캣 내 세션 복제보다는 IMDG 또는 외부 세션 스토어 아키텍처를 기본 옵션으로 두고 비교하는 것을 추천합니다.[2][3][4]

출처
[1] Apache Tomcat 9 (9.0.115) - Clustering/Session Replication ... https://tomcat.apache.org/tomcat-9.0-doc/cluster-howto.html
[2] Infinispan for HTTP session clustering and caching https://docs.jboss.org/author/display/ISPN53/Infinispan%20for%20HTTP%20session%20clustering%20and%20caching.html
[3] Oracle Coherence - In-Memory Data Grid https://www.oracle.com/java/coherence/
[4] in-memory data grid 보관 - IT Garage https://www.sierracloud.kro.kr/tag/in-memory-data-grid/
[5] How It Works https://tomcat.apache.org/tomcat-10.1-doc/cluster-howto.html
[6] Tomcat Session Clustering 방식 https://velog.io/@maestroks/Tomcat-Session-Clustering-%EB%B0%A9%EC%8B%9D
[7] Tomcat Session Clustering 설정 - Nate의 IT블로그 https://eng-nate.tistory.com/13
[8] What are the drawbacks of session replication on Tomcat? https://stackoverflow.com/questions/3040296/what-are-the-drawbacks-of-session-replication-on-tomcat
[9] Apache Tomcat 7 (7.0.99) - Clustering/Session Replication ... https://www.ekacem.or.kr/docs/cluster-howto.html
[10] Apache Tomcat 7 (7.0.103) - Clustering/Session ... https://nonsancntf.or.kr/docs/cluster-howto.html
[11] Tomcat8 - 세션 클러스터링(Session Clustering) 가이드 https://samso.tistory.com/entry/Tomcat8-%EC%84%B8%EC%85%98-%ED%81%B4%EB%9F%AC%EC%8A%A4%ED%84%B0%EB%A7%81
[12] HTTP Session Replication for Tomcat Web-server (May 2012) https://simoes.org/Site/DynamoTomcatWhitePaper.pdf
[13] Tomcat external session store and WebRatio webapp. https://my.webratio.com/forum/question-details/tomcat-external-session-store-and-webratio-webapp?link=ln27d
[14] WebSphere Liberty Profile Cluster Sharing an In-Memory Data Grid https://www.stormacq.com/old/websphere-liberty-profile-cluster-sharing-an-in-memory-data-grid/index.html
[15] 37. Clustering and Session Replication in Tomcat 9 https://www.youtube.com/watch?v=z0OfwLPQipM
