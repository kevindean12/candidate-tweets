-- MySQL database creation statements for the database associated with Candidates_Data_Collection.ipynb
CREATE TABLE Twitter_User_T
    (
        UserID MEDIUMINT UNSIGNED NOT NULL,
        UserName VARCHAR(200) NOT NULL,
        TwitterHandle VARCHAR(200) NOT NULL,
        CONSTRAINT Twitter_User_PK PRIMARY KEY(UserID)
    );

CREATE TABLE Candidate_T
    (
        CandidateID MEDIUMINT UNSIGNED NOT NULL,
        CandidateLastName VARCHAR(100) NOT NULL,
        CandidateFirstName VARCHAR(100) NOT NULL,
        DateAnnounced DATE,
        Party VARCHAR(50),
        CONSTRAINT Candidate_PK PRIMARY KEY(CandidateID),
        CONSTRAINT Candidate_FK FOREIGN KEY (CandidateID) REFERENCES Twitter_User_T(UserID)
    );

CREATE TABLE Topic_T
    (
        TopicNum MEDIUMINT UNSIGNED NOT NULL,
        TopicName VARCHAR(500),
        CONSTRAINT Topic_PK PRIMARY KEY(TopicNum)
    );

CREATE TABLE Keyword_T
    (
        TopicNum MEDIUMINT UNSIGNED NOT NULL,
        Keyword VARCHAR(300) NOT NULL,
        CONSTRAINT PRIMARY KEY(TopicNum, Keyword),
        CONSTRAINT Keyword_FK FOREIGN KEY (TopicNum) REFERENCES Topic_T(TopicNum)
    );

CREATE TABLE Tweet_T
    (
        TweetID VARCHAR(100) NOT NULL,
        LengthWords INT,
        TweetFullText VARCHAR(1000),
        TweetDate DATE,
        TimesRetweeted INT,
        TweetDominantTopic MEDIUMINT UNSIGNED,
        UserID MEDIUMINT UNSIGNED,
        CONSTRAINT Tweet_PK PRIMARY KEY(TweetID),
        CONSTRAINT Tweet_FK_1 FOREIGN KEY(TweetDominantTopic) REFERENCES Topic_T(TopicNum),
        CONSTRAINT Tweet_FK_2 FOREIGN KEY(UserID) REFERENCES Twitter_User_T(UserID)
    );

CREATE TABLE User_Mention_T
    (
        UserID MEDIUMINT UNSIGNED NOT NULL,
        CandidateID MEDIUMINT UNSIGNED NOT NULL,
        TweetID VARCHAR(100) NOT NULL,
        CONSTRAINT User_Mention_PK PRIMARY KEY(UserID, CandidateID, TweetID),
        CONSTRAINT User_Mention_FK_1 FOREIGN KEY(UserID) REFERENCES Twitter_User_T(UserID),
        CONSTRAINT User_Mention_FK_2 FOREIGN KEY(CandidateID) REFERENCES Candidate_T(CandidateID)
    );

CREATE TABLE Retweet_T
    (
        UserID MEDIUMINT UNSIGNED NOT NULL,
        TweetID VARCHAR(100) NOT NULL,
        OriginalTweetDate Date NOT NULL,
        CONSTRAINT Retweet_PK PRIMARY KEY(UserID, TweetID, OriginalTweetDate),
        CONSTRAINT Retweet_FK_1 FOREIGN KEY(UserID) REFERENCES Twitter_User_T(UserID),
        CONSTRAINT Retweet_FK_2 FOREIGN KEY(TweetID) REFERENCES Tweet_T(TweetID)
    );

CREATE TABLE NGramToken_T
    (
        TokenID MEDIUMINT UNSIGNED NOT NULL,
        TokenText VARCHAR(200),
        PartOfSpeech VARCHAR(100),
        TokenLemma VARCHAR(200),
        CONSTRAINT NGramToken_PK PRIMARY KEY(TokenID)
    );

CREATE TABLE TokenInTweet_T
    (
        TweetID VARCHAR(100) NOT NULL,
        TokenID MEDIUMINT UNSIGNED NOT NULL,
        CONSTRAINT TokenInTweet_PK PRIMARY KEY(TokenID, TweetID),
        CONSTRAINT TokenInTweet_FK_1 FOREIGN KEY(TokenID) REFERENCES NGramToken_T(TokenID),
        CONSTRAINT TokenInTweet_FK_2 FOREIGN KEY(TweetID) REFERENCES Tweet_T(TweetID)
    );

CREATE TABLE NewsSource_T
    (
        NewsID MEDIUMINT UNSIGNED NOT NULL,
        NewsName VARCHAR(200), 
        UserID MEDIUMINT UNSIGNED,
        CONSTRAINT NewsSource_PK PRIMARY KEY(NewsID),
        CONSTRAINT NewsSource_FK FOREIGN KEY(UserID) REFERENCES Twitter_User_T(UserID)
    );

CREATE TABLE Headline_T
    (
        ArticleID MEDIUMINT UNSIGNED NOT NULL,
        ArticleHeadline TEXT,
        ArticleDescription TEXT,
        DatePublished DATE,
        NewsID MEDIUMINT UNSIGNED,
        HeadlineDominantTopic MEDIUMINT UNSIGNED,
        CONSTRAINT Headline_PK PRIMARY KEY(ArticleID),
        CONSTRAINT Headline_FK_1 FOREIGN KEY(NewsID) REFERENCES NewsSource_T(NewsID),
        CONSTRAINT Headline_FK_2 FOREIGN KEY(HeadlineDominantTopic) REFERENCES Topic_T(TopicNum)
    );

CREATE TABLE ArticleAboutCandidate_T
    (
        ArticleID MEDIUMINT UNSIGNED NOT NULL,
        CandidateID MEDIUMINT UNSIGNED NOT NULL,
        CONSTRAINT ArticleAboutCandidate_PK PRIMARY KEY(ArticleID, CandidateID),
        CONSTRAINT ArticleAboutCandidate_FK_1 FOREIGN KEY(ArticleID) REFERENCES Headline_T(ArticleID),
        CONSTRAINT ArticleAboutCandidate_FK_2 FOREIGN KEY(CandidateID) REFERENCES Candidate_T(CandidateID)
    );

CREATE TABLE TokenInHeadline_T
    (
        TokenID MEDIUMINT UNSIGNED NOT NULL,
        ArticleID MEDIUMINT UNSIGNED NOT NULL,
        CONSTRAINT TokenInHeadline_PK PRIMARY KEY(TokenID, ArticleID),
        CONSTRAINT TokenInHeadline_FK_1 FOREIGN KEY(TokenID) REFERENCES NGramToken_T(TokenID),
        CONSTRAINT TokenInHeadline_FK_2 FOREIGN KEY(ArticleID) REFERENCES Headline_T(ArticleID)
    );

CREATE TABLE Link_T
    (
        LinkID MEDIUMINT UNSIGNED NOT NULL,
        LinkURL VARCHAR(500),
        SourceName VARCHAR(200),
        CONSTRAINT Link_PK PRIMARY KEY(LinkID)
    );

CREATE TABLE LinkInstanceTweet_T
    (
        LinkID MEDIUMINT UNSIGNED NOt NULL,
        TweetID VARCHAR(100) NOt NULL,
        CONSTRAINT LinkInstanceTweet_PK PRIMARY KEY(LinkID, TweetID),
        CONSTRAINT LinkInstanceTweet_FK_1 FOREIGN KEY(LinkID) REFERENCES Link_T(LinkID),
        CONSTRAINT LinkInstanceTweet_FK_2 FOREIGN KEY(TweetID) REFERENCES Tweet_T(TweetID)
    );

CREATE TABLE Hashtag_T
    (
        HashtagID MEDIUMINT UNSIGNED NOt NULL,
        HashtagName VARCHAR(200),
        CONSTRAINT Hashtag_PK PRIMARY KEY(HashtagID)
    );

CREATE TABLE HashtagInTweet_T
    (
        HashtagID MEDIUMINT UNSIGNED NOt NULL,
        TweetID VARCHAR(100) NOt NULL,
        CONSTRAINT HashtagInTweet_PK PRIMARY KEY(HashtagID, TweetID),
        CONSTRAINT HashtagInTweet_FK_1 FOREIGN KEY(HashtagID) REFERENCES Hashtag_T(HashtagID),
        CONSTRAINT HashtagInTweet_FK_2 FOREIGN KEY(TweetID) REFERENCES Tweet_T(TweetID)
    );

CREATE TABLE TopicInTweet_T
    (
        TopicNum MEDIUMINT UNSIGNED NOT NULL,
        TweetID VARCHAR(100) NOT NULL,
        CONSTRAINT TopicInTweet_PK PRIMARY KEY(TopicNum, TweetID),
        CONSTRAINT TopicInTweet_FK_1 FOREIGN KEY(TopicNum) REFERENCES Topic_T(TopicNum),
        CONSTRAINT TopicInTweet_FK_2 FOREIGN KEY(TweetID) REFERENCES Tweet_T(TweetID)
    );

CREATE TABLE TopicInHeadline_T
    (
        TopicNum MEDIUMINT UNSIGNED NOT NULL,
        ArticleID MEDIUMINT UNSIGNED NOT NULL,
        CONSTRAINT TopicInHeadline_PK PRIMARY KEY(TopicNum, ArticleID),
        CONSTRAINT TopicInHeadline_FK_1 FOREIGN KEY(TopicNum) REFERENCES Topic_T(TopicNum),
        CONSTRAINT TopicInHeadline_FK_2 FOREIGN KEY(ArticleID) REFERENCES Headline_T(ArticleID)
    );

